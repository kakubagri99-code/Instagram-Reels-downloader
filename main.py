#!/usr/bin/env python3
"""
Command-line interface for Instagram Reels Downloader
"""

import argparse
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from reels_downloader import InstagramReelsDownloader


def main():
    """Main CLI function"""
    
    # Load environment variables
    load_dotenv()
    
    parser = argparse.ArgumentParser(
        description='Download Instagram Reels easily',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Download single reel by URL
  python main.py --url "https://www.instagram.com/reel/ABC123/"
  
  # Download by reel ID
  python main.py --id "ABC123"
  
  # Download multiple from file
  python main.py --urls reels.txt --output ./my_downloads
  
  # With authentication
  python main.py --url "https://www.instagram.com/reel/ABC123/" --username your_user --password your_pass
        '''
    )
    
    parser.add_argument('--url', type=str, help='Instagram reel URL')
    parser.add_argument('--id', type=str, help='Instagram reel ID')
    parser.add_argument('--urls', type=str, help='File with reel URLs (one per line)')
    parser.add_argument('--output', type=str, default='./downloads',
                       help='Output directory (default: ./downloads)')
    parser.add_argument('--username', type=str, 
                       default=os.getenv('INSTAGRAM_USERNAME'),
                       help='Instagram username for private content')
    parser.add_argument('--password', type=str,
                       default=os.getenv('INSTAGRAM_PASSWORD'),
                       help='Instagram password for private content')
    parser.add_argument('--no-metadata', action='store_true',
                       help='Don\'t save metadata JSON files')
    parser.add_argument('--retries', type=int, default=3,
                       help='Maximum retry attempts (default: 3)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.url, args.id, args.urls]):
        parser.print_help()
        print("\n❌ Error: Please provide --url, --id, or --urls")
        sys.exit(1)
    
    # Initialize downloader
    print("🚀 Instagram Reels Downloader")
    print("=" * 50)
    
    downloader = InstagramReelsDownloader(args.username, args.password)
    
    try:
        # Determine what to download
        if args.url:
            # Single URL
            print(f"\n��� Target: {args.url}")
            success = downloader.download_reel(
                args.url,
                args.output,
                not args.no_metadata
            )
            sys.exit(0 if success else 1)
            
        elif args.id:
            # Single ID
            print(f"\n📍 Target: {args.id}")
            success = downloader.download_reel(
                args.id,
                args.output,
                not args.no_metadata
            )
            sys.exit(0 if success else 1)
            
        elif args.urls:
            # Multiple from file
            if not Path(args.urls).exists():
                print(f"❌ File not found: {args.urls}")
                sys.exit(1)
            
            print(f"\n📁 Loading reels from: {args.urls}")
            results = downloader.download_from_file(
                args.urls,
                args.output,
                not args.no_metadata
            )
            
            # Print summary
            successful = sum(1 for v in results.values() if v)
            total = len(results)
            
            print("\n" + "=" * 50)
            print(f"📊 Download Summary")
            print(f"✓ Successful: {successful}/{total}")
            print(f"✗ Failed: {total - successful}/{total}")
            
            if successful == total:
                print("\n✅ All reels downloaded successfully!")
                sys.exit(0)
            else:
                print("\n⚠️  Some reels failed to download")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n\n⏹️  Download interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
    finally:
        if downloader.authenticated:
            downloader.logout()


if __name__ == '__main__':
    main()
