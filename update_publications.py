#!/usr/bin/env python3
"""
Google Scholar Publication Updater
Scrapes Google Scholar profile and updates publications.json

Installation:
    pip install scholarly

Usage:
    python update_publications.py

Author: Ahmad Luky Ramdani
"""

import json
from datetime import datetime
import os

# Uncomment after installing scholarly:
from scholarly import scholarly

def get_scholar_profile(scholar_id):
    """
    Fetch publications from Google Scholar profile
    
    Args:
        scholar_id: Google Scholar user ID (from profile URL)
    
    Returns:
        Dictionary with profile data and publications
    """
    try:
        # Uncomment these lines after installing scholarly:
        search_query = scholarly.search_author_id(scholar_id)
        author = scholarly.fill(search_query)
        
        publications_list = []
        for pub in author['publications']:
            pub_filled = scholarly.fill(pub)
            publications_list.append({
                'title': pub_filled['bib']['title'],
                'authors': pub_filled['bib'].get('author', ''),
                'venue': pub_filled['bib'].get('venue', 'N/A'),
                'year': int(pub_filled['bib'].get('pub_year', datetime.now().year)),
                'citations': pub_filled.get('num_citations', 0),
                'pdfUrl': pub_filled.get('eprint_url', ''),
                'type': 'journal' if 'journal' in pub_filled['bib'].get('venue', '').lower() else 'conference'
            })
        
        return {
            'totalCitations': author.get('citedby', 0),
            'publications': publications_list
        }
        
        # Temporary placeholder - replace with actual data
        print("⚠️  Scholarly library not installed.")
        print("Install with: pip install scholarly")
        return None
        
    except Exception as e:
        print(f"Error fetching Scholar data: {e}")
        return None

def update_publications_json(scholar_id, output_file='data/publications.json'):
    """
    Update publications.json file with latest data from Google Scholar
    """
    print(f"🔍 Fetching publications for Scholar ID: {scholar_id}")
    
    scholar_data = get_scholar_profile(scholar_id)
    
    if scholar_data is None:
        print("❌ Could not fetch data. Using manual mode.")
        print("\n📝 Please manually edit data/publications.json")
        print("   See the example structure in the file.")
        return False
    
    # Load existing data to preserve presentations
    existing_data = {}
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except:
            pass
    
    # Merge data
    updated_data = {
        'lastUpdated': datetime.now().strftime('%Y-%m-%d'),
        'scholarProfile': f'https://scholar.google.com/citations?user={scholar_id}',
        'totalCitations': scholar_data.get('totalCitations', 0),
        'publications': scholar_data.get('publications', []),
        'presentations': existing_data.get('presentations', [])
    }
    
    # Save to file
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Successfully updated {output_file}")
    print(f"   - {len(updated_data['publications'])} publications")
    print(f"   - {updated_data['totalCitations']} total citations")
    print(f"   - {len(updated_data['presentations'])} presentations")
    
    return True

def manual_add_publication():
    """
    Interactive mode to manually add a publication
    """
    print("\n📝 Manual Publication Entry")
    print("-" * 50)
    
    pub = {
        'title': input("Judul publikasi: "),
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
    data['lastUpdated'] = datetime.now().strftime('%Y-%m-%d')
    
    # Save
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Publikasi ditambahkan ke {output_file}")

def main():
    """Main function"""
    print("=" * 50)
    print("📚 Google Scholar Publication Updater")
    print("=" * 50)
    
    # Your Google Scholar ID
    SCHOLAR_ID = "gjOzo9MAAAAJ"
    
    print("\nPilih mode:")
    print("1. Auto-fetch dari Google Scholar (requires 'scholarly' library)")
    print("2. Manual entry")
    print("3. Edit file JSON langsung")
    
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
