#!/usr/bin/env python3
"""
Google Scholar Publication Updater v2
Improved version with proxy support and better error handling

Installation:
    pip install scholarly free-proxy

Usage:
    python update_publications_v2.py

Author: Ahmad Luky Ramdani
"""

import json
from datetime import datetime
import os
import time
import sys

try:
    from scholarly import scholarly, ProxyGenerator
except ImportError:
    print("❌ Error: 'scholarly' library not found")
    print("Install with: pip install scholarly")
    sys.exit(1)

def setup_proxy():
    """Setup proxy to avoid Google Scholar blocking"""
    print("🔧 Setting up proxy to bypass Google Scholar blocking...")
    try:
        pg = ProxyGenerator()
        
        # Try FreeProxies first
        print("   Trying free proxies...")
        if pg.FreeProxies():
            scholarly.use_proxy(pg)
            print("✅ Free proxy configured successfully!")
            return True
        
        # If that fails, try Tor (if available)
        print("   Free proxies failed, trying Tor...")
        if pg.Tor_Internal(tor_cmd="tor"):
            scholarly.use_proxy(pg)
            print("✅ Tor proxy configured successfully!")
            return True
        
        print("⚠️  All proxy methods failed, continuing without proxy...")
        return False
        
    except Exception as e:
        print(f"⚠️  Proxy setup error: {e}")
        print("   Continuing without proxy (may be blocked by Google)...")
        return False

def get_scholar_profile_with_retry(scholar_id, max_retries=3, use_proxy=True):
    """
    Fetch publications from Google Scholar with retry logic
    
    Args:
        scholar_id: Google Scholar user ID
        max_retries: Maximum number of retry attempts
        use_proxy: Whether to use proxy
    
    Returns:
        Dictionary with profile data and publications
    """
    for attempt in range(1, max_retries + 1):
        print(f"\n{'='*60}")
        print(f"🔄 Attempt {attempt} of {max_retries}")
        print(f"{'='*60}")
        
        try:
            # Setup proxy on first attempt or if previous attempt failed
            if use_proxy and attempt == 1:
                setup_proxy()
            
            print(f"\n🔍 Searching for author ID: {scholar_id}")
            search_query = scholarly.search_author_id(scholar_id)
            
            print("📥 Fetching author profile...")
            author = scholarly.fill(search_query)
            
            author_name = author.get('name', 'Unknown')
            print(f"✅ Found author: {author_name}")
            print(f"📊 Total citations: {author.get('citedby', 0)}")
            
            publications_list = []
            total_pubs = len(author.get('publications', []))
            print(f"📚 Found {total_pubs} publications. Fetching details...")
            print("-" * 60)
            
            for idx, pub in enumerate(author['publications'], 1):
                try:
                    print(f"\n[{idx}/{total_pubs}] ", end='')
                    
                    # Fetch publication details
                    pub_filled = scholarly.fill(pub)
                    
                    # Extract title
                    title = pub_filled['bib'].get('title', 'Untitled')
                    print(f"✓ {title}")
                    
                    # Handle authors (can be string or list)
                    authors = pub_filled['bib'].get('author', '')
                    if isinstance(authors, list):
                        authors = ', '.join(authors)
                    
                    # Extract venue
                    venue = pub_filled['bib'].get('venue', 'N/A')
                    year = int(pub_filled['bib'].get('pub_year', datetime.now().year))
                    citations = pub_filled.get('num_citations', 0)
                    
                    print(f"    Authors: {authors[:80]}...")
                    print(f"    Venue: {venue}")
                    print(f"    Year: {year} | Citations: {citations}")
                    
                    publications_list.append({
                        'title': title,
                        'authors': authors,
                        'venue': venue,
                        'year': year,
                        'citations': citations,
                        'pdfUrl': pub_filled.get('eprint_url', ''),
                        'type': 'journal' if 'journal' in venue.lower() else 'conference'
                    })
                    
                    # IMPORTANT: Add delay to avoid rate limiting
                    if idx < total_pubs:  # Don't wait after last item
                        wait_time = 3
                        print(f"    ⏳ Waiting {wait_time}s to avoid rate limiting...")
                        time.sleep(wait_time)
                    
                except Exception as pub_error:
                    print(f"⚠️  Error processing publication {idx}: {pub_error}")
                    print("    Skipping this publication...")
                    continue
            
            result = {
                'totalCitations': author.get('citedby', 0),
                'publications': publications_list,
                'authorName': author_name
            }
            
            print("\n" + "="*60)
            print(f"✅ SUCCESS! Fetched {len(publications_list)} publications")
            print(f"📊 Total citations: {result['totalCitations']}")
            print("="*60)
            
            return result
            
        except Exception as e:
            print(f"\n❌ Attempt {attempt} failed: {e}")
            
            if attempt < max_retries:
                wait_time = 30 * attempt  # Exponential backoff
                print(f"⏳ Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                print("🔄 Retrying with fresh connection...")
            else:
                print("\n💥 All attempts failed!")
                print("\n💡 Solutions:")
                print("   1. Wait 10-15 minutes (Google may be temporarily blocking)")
                print("   2. Use a VPN and try again")
                print("   3. Try on a different network (mobile hotspot, etc.)")
                print("   4. Use manual entry mode instead (option 2)")
                return None
    
    return None

def update_publications_json(scholar_id, output_file='data/publications.json'):
    """
    Update publications.json file with latest data from Google Scholar
    """
    print("\n" + "="*60)
    print("📚 GOOGLE SCHOLAR PUBLICATION UPDATER")
    print("="*60)
    print(f"Scholar ID: {scholar_id}")
    print(f"Output file: {output_file}")
    
    # Fetch data with retry
    scholar_data = get_scholar_profile_with_retry(scholar_id, max_retries=3, use_proxy=True)
    
    if scholar_data is None:
        print("\n❌ Could not fetch data from Google Scholar")
        print("📝 Please use manual entry mode or edit JSON directly")
        return False
    
    # Load existing data to preserve presentations
    existing_data = {}
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            print(f"\n📂 Loaded existing data from {output_file}")
        except Exception as e:
            print(f"⚠️  Could not load existing data: {e}")
    
    # Merge data
    updated_data = {
        'lastUpdated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'scholarProfile': f'https://scholar.google.com/citations?user={scholar_id}',
        'authorName': scholar_data.get('authorName', 'Unknown'),
        'totalCitations': scholar_data.get('totalCitations', 0),
        'publications': scholar_data.get('publications', []),
        'presentations': existing_data.get('presentations', [])
    }
    
    # Save to file
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, indent=2, ensure_ascii=False)
        
        print("\n" + "="*60)
        print(f"✅ SUCCESSFULLY UPDATED {output_file}")
        print("="*60)
        print(f"📚 Publications: {len(updated_data['publications'])}")
        print(f"📊 Total Citations: {updated_data['totalCitations']}")
        print(f"🎤 Presentations: {len(updated_data['presentations'])}")
        print(f"🕐 Last Updated: {updated_data['lastUpdated']}")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error saving file: {e}")
        return False

def manual_add_publication():
    """
    Interactive mode to manually add a publication
    """
    print("\n" + "="*60)
    print("📝 MANUAL PUBLICATION ENTRY")
    print("="*60)
    
    pub = {
        'title': input("\nJudul publikasi: "),
        'authors': input("Penulis (pisahkan dengan koma): "),
        'venue': input("Nama jurnal/konferensi: "),
        'year': int(input("Tahun publikasi: ")),
        'citations': int(input("Jumlah sitasi (0 jika tidak ada): ")),
        'pdfUrl': input("URL PDF (kosongkan jika tidak ada): "),
        'type': input("Tipe (journal/conference): ")
    }
    
    # Load existing data
    output_file = 'data/publications.json'
    data = {'publications': [], 'presentations': []}
    
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    
    # Add new publication
    data['publications'].append(pub)
    data['lastUpdated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Save
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Publikasi ditambahkan ke {output_file}")

def main():
    """Main function"""
    print("\n" + "="*60)
    print("📚 GOOGLE SCHOLAR PUBLICATION UPDATER v2")
    print("="*60)
    print("Enhanced version with:")
    print("  • Proxy support to bypass blocking")
    print("  • Automatic retry with backoff")
    print("  • Better error handling")
    print("="*60)
    
    # Your Google Scholar ID
    SCHOLAR_ID = "gjOzo9MAAAAJ"
    
    print("\n📋 Pilih mode:")
    print("=" * 60)
    print("1. Auto-fetch dari Google Scholar (with proxy & retry)")
    print("2. Manual entry (input publikasi satu per satu)")
    print("3. Edit file JSON langsung")
    print("=" * 60)
    
    choice = input("\nPilihan (1/2/3): ").strip()
    
    if choice == "1":
        update_publications_json(SCHOLAR_ID)
    elif choice == "2":
        manual_add_publication()
    else:
        output_file = 'data/publications.json'
        print(f"\n📝 Silakan edit file: {output_file}")
        print("   Struktur JSON sudah tersedia di file tersebut.")
        
        # Open file in default editor (macOS)
        if os.path.exists(output_file):
            os.system(f'open "{output_file}"')

if __name__ == "__main__":
    main()
