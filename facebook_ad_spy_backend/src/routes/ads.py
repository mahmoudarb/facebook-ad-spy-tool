from flask import Blueprint, request, jsonify
from datetime import datetime
import asyncio
import threading
from src.models.user import db
from src.models.page import Page
from src.models.ad import Ad
from src.models.scraping_job import ScrapingJob
from src.scraper.facebook_scraper import scrape_facebook_ads
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ads_bp = Blueprint('ads', __name__)

@ads_bp.route('/pages', methods=['GET'])
def get_pages():
    """Get all scraped pages"""
    try:
        pages = Page.query.all()
        return jsonify({
            'success': True,
            'pages': [page.to_dict() for page in pages]
        })
    except Exception as e:
        logger.error(f"Error getting pages: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@ads_bp.route('/ads', methods=['GET'])
def get_ads():
    """Get ads with optional filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        page_id = request.args.get('page_id')
        search_term = request.args.get('search')
        platform = request.args.get('platform')
        
        query = Ad.query
        
        # Apply filters
        if page_id:
            query = query.filter(Ad.page_id == page_id)
        
        if search_term:
            query = query.filter(Ad.ad_text.contains(search_term))
        
        if platform:
            query = query.filter(Ad.platforms.contains(platform))
        
        # Order by scraped_at descending
        query = query.order_by(Ad.scraped_at.desc())
        
        # Paginate
        ads_pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'ads': [ad.to_dict() for ad in ads_pagination.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': ads_pagination.total,
                'pages': ads_pagination.pages,
                'has_next': ads_pagination.has_next,
                'has_prev': ads_pagination.has_prev
            }
        })
    except Exception as e:
        logger.error(f"Error getting ads: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@ads_bp.route('/scrape', methods=['POST'])
def start_scraping():
    """Start scraping job for given page IDs"""
    try:
        data = request.get_json()
        page_ids = data.get('page_ids', [])
        max_ads_per_page = data.get('max_ads_per_page')
        
        if not page_ids:
            return jsonify({'success': False, 'error': 'No page IDs provided'}), 400
        
        # Create scraping job
        job = ScrapingJob()
        job.set_page_ids_list(page_ids)
        job.status = 'pending'
        db.session.add(job)
        db.session.commit()
        
        # Start scraping in background thread
        thread = threading.Thread(
            target=run_scraping_job,
            args=(job.id, page_ids, max_ads_per_page)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'job_id': job.id,
            'message': f'Scraping started for {len(page_ids)} pages'
        })
        
    except Exception as e:
        logger.error(f"Error starting scraping: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@ads_bp.route('/jobs/<int:job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get scraping job status"""
    try:
        job = ScrapingJob.query.get_or_404(job_id)
        return jsonify({
            'success': True,
            'job': job.to_dict()
        })
    except Exception as e:
        logger.error(f"Error getting job status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@ads_bp.route('/jobs', methods=['GET'])
def get_jobs():
    """Get all scraping jobs"""
    try:
        jobs = ScrapingJob.query.order_by(ScrapingJob.created_at.desc()).all()
        return jsonify({
            'success': True,
            'jobs': [job.to_dict() for job in jobs]
        })
    except Exception as e:
        logger.error(f"Error getting jobs: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def run_scraping_job(job_id, page_ids, max_ads_per_page=None):
    """Run scraping job in background"""
    from src.main import app
    
    with app.app_context():
        try:
            # Update job status
            job = ScrapingJob.query.get(job_id)
            job.status = 'running'
            job.started_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Starting scraping job {job_id} for {len(page_ids)} pages")
            
            # Run the async scraper
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(
                scrape_facebook_ads(page_ids, max_ads_per_page)
            )
            loop.close()
            
            # Process results and save to database
            total_ads_saved = 0
            for result in results:
                page_id = result['page_id']
                page_name = result['page_name']
                ads = result['ads']
                error = result['error']
                
                # Create or update page record
                page = Page.query.filter_by(page_id=page_id).first()
                if not page:
                    page = Page(page_id=page_id)
                    db.session.add(page)
                
                page.page_name = page_name or page.page_name
                page.last_scraped = datetime.utcnow()
                page.status = 'completed' if not error else 'error'
                
                # Save ads
                if ads:
                    for ad_data in ads:
                        # Check if ad already exists
                        existing_ad = Ad.query.filter_by(library_id=ad_data['library_id']).first()
                        if not existing_ad:
                            ad = Ad(
                                page_id=page_id,
                                library_id=ad_data['library_id'],
                                ad_text=ad_data['ad_text'],
                                media_url=ad_data['media_url'],
                                media_type=ad_data['media_type'],
                                start_date=ad_data['start_date'],
                                cta=ad_data['cta']
                            )
                            ad.set_platforms_list(ad_data['platforms'])
                            db.session.add(ad)
                            total_ads_saved += 1
            
            db.session.commit()
            
            # Update job status
            job.status = 'completed'
            job.completed_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Scraping job {job_id} completed. Saved {total_ads_saved} new ads")
            
        except Exception as e:
            logger.error(f"Error in scraping job {job_id}: {str(e)}")
            
            # Update job with error
            job = ScrapingJob.query.get(job_id)
            job.status = 'error'
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.session.commit()

@ads_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get overall statistics"""
    try:
        total_pages = Page.query.count()
        total_ads = Ad.query.count()
        recent_jobs = ScrapingJob.query.order_by(ScrapingJob.created_at.desc()).limit(5).all()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_pages': total_pages,
                'total_ads': total_ads,
                'recent_jobs': [job.to_dict() for job in recent_jobs]
            }
        })
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

