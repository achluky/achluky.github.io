#!/usr/bin/env python3
"""
Simple Google Scholar Scraper (No Proxy)
Alternatif tanpa proxy - lebih lambat tapi lebih stabil

Installation:
    pip install scholarly

Usage:
    python simple_update.py

Author: Ahmad Luky Ramdani
"""

import json
from datetime import datetime
import os
import time

try:
    from scholarly import scholarly
except ImportError:
    print("❌ Library 'scholarly' belum terinstall")
    print("Install dengan: pip install scholarly")
    exit(1)

# Konfigurasi
SCHOLAR_ID = "gjOzo9MAAAAJ"
OUTPUT_FILE = "data/publications.json"
DELAY_BETWEEN_PUBS = 5  # detik (lebih lama = lebih aman)

def fetch_publications_simple():
    """Fetch publikasi dengan cara yang lebih aman (tanpa proxy)"""
    
    print("="*70)
    print("📚 SIMPLE GOOGLE SCHOLAR UPDATER (No Proxy)")
    print("="*70)
    print("⚠️  CATATAN: Proses ini LAMBAT untuk menghindari blocking")
    print(f"   Delay antar publikasi: {DELAY_BETWEEN_PUBS} detik")
    print("="*70)
    
    try:
        # Step 1: Get author
        print(f"\n🔍 Step 1: Mencari author {SCHOLAR_ID}...")
        author_query = scholarly.search_author_id(SCHOLAR_ID)
        
        print("📥 Step 2: Mengambil data author...")
        time.sleep(3)  # Wait before filling
        author = scholarly.fill(author_query)
        
        author_name = author.get('name', 'Unknown')
        total_citations = author.get('citedby', 0)
        
        print(f"✅ Author: {author_name}")
        print(f"📊 Total citations: {total_citations}")
        
        # Step 2: Get publications (basic info only)
        publications = author.get('publications', [])
        total_pubs = len(publications)
        print(f"\n📚 Step 3: Memproses {total_pubs} publikasi...")
        print("   (Ini akan memakan waktu...)")
        print("-"*70)
        
        publications_list = []
        
        for idx, pub in enumerate(publications[:10], 1):  # Limit to 10 publikasi terakhir
            try:
                print(f"\n[{idx}/10] ", end='')
                
                # Get basic info (usually available without filling)
                bib = pub.get('bib', {})
                title = bib.get('title', 'Untitled')
                
                print(f"Processing: {title[:60]}...")
                
                # Try to fill (might fail due to rate limiting)
                try:
                    time.sleep(DELAY_BETWEEN_PUBS)
                    pub_filled = scholarly.fill(pub)
                    bib = pub_filled['bib']
                    citations = pub_filled.get('num_citations', 0)
                except Exception as fill_error:
                    print(f"    ⚠️  Could not fetch full details: {fill_error}")
                    print("    Using basic info only...")
                    citations = pub.get('num_citations', 0)
                
                # Extract data
                authors = bib.get('author', '')
                if isinstance(authors, list):
                    authors = ', '.join(authors)
                
                venue = bib.get('venue', 'N/A')
                year = int(bib.get('pub_year', datetime.now().year))
                
                pub_data = {
                    'title': title,
                    'authors': authors,
                    'venue': venue,
                    'year': year,
                    'citations': citations,
                    'pdfUrl': pub.get('eprint_url', ''),
                    'type': 'journal' if 'journal' in venue.lower() else 'conference'
                }
                
                publications_list.append(pub_data)
                
                print(f"    ✓ Added: {year} | {citations} citations")
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
                print("    Skipping...")
                continue
        
        print("\n" + "="*70)
        print(f"✅ Berhasil mengambil {len(publications_list)} publikasi")
        print("="*70)
        
        return {
            'authorName': author_name,
            'totalCitations': total_citations,
            'publications': publications_list
        }
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\n💡 Solusi:")
        print("   1. Tunggu 15-30 menit lalu coba lagi")
        print("   2. Gunakan VPN/network lain")
        print("   3. Edit manual file JSON")
        return None

def save_publications(data):
    """Simpan data ke JSON"""
    if not data:
        return False
    
    # Load existing data
    existing_data = {}
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except:
            pass
    
    # Merge
    updated_data = {
        'lastUpdated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'scholarProfile': f'https://scholar.google.com/citations?user={SCHOLAR_ID}',
        'authorName': data.get('authorName', 'Unknown'),
        'totalCitations': data.get('totalCitations', 0),
        'publications': data.get('publications', []),
        'presentations': existing_data.get('presentations', [])
    }
    
    # Save
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Data disimpan ke: {OUTPUT_FILE}")
    print(f"   - {len(updated_data['publications'])} publications")
    print(f"   - {updated_data['totalCitations']} total citations")
    
    return True

if __name__ == "__main__":
    print("\n⏰ PERHATIAN: Script ini akan berjalan lambat (delay {DELAY_BETWEEN_PUBS}s/publikasi)")
    print("   untuk menghindari blocking dari Google Scholar")
    
    input("\nTekan ENTER untuk mulai...")
    
    data = fetch_publications_simple()
    
    if data:
        save_publications(data)
        print("\n🎉 SELESAI!")
    else:
        print("\n❌ Gagal mengambil data. Silakan coba lagi nanti.")
