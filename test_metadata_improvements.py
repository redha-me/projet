#!/usr/bin/env python3
"""
test_metadata_improvements.py - Test the improved metadata system
"""

import sys
from pathlib import Path

# Add webapp to path
sys.path.insert(0, str(Path(__file__).parent / "webapp"))

from recommender import BookRecommender

print("=" * 70)
print(" TESTING IMPROVED METADATA SYSTEM")
print("=" * 70)

# Load recommender
try:
    recommender = BookRecommender()
    print("\n✅ BookRecommender loaded successfully\n")
except Exception as e:
    print(f"\n❌ Failed to load BookRecommender: {e}")
    sys.exit(1)

# Test metadata quality tracking
print(f"Total books: {recommender.get_book_count()}")
print(f"Total users: {recommender.get_user_count()}")

# Sample a few books
test_book_indices = [0, 5, 10, 50, 100, 200, 500, 800]

print("\n" + "=" * 70)
print("SAMPLE BOOK METADATA TEST")
print("=" * 70)

for book_idx in test_book_indices:
    if book_idx >= recommender.get_book_count():
        continue
    
    meta = recommender.get_book_meta(book_idx)
    
    print(f"\n📖 Book #{book_idx}: {meta['title'][:60]}")
    print(f"   Author: {meta['author']}")
    print(f"   Genre: {meta['genre']}")
    print(f"   Quality: {meta.get('metadata_quality', 'unknown')}")
    
    # Check if image URL is generated or real
    if meta['image_url']:
        if 'dummyimage.com' in meta['image_url'] or 'placehold.co' in meta['image_url']:
            print(f"   Image: 🎨 Generated placeholder (colorful)")
        else:
            print(f"   Image: 📸 Real cover image")
    
    if meta.get('goodreads_url'):
        print(f"   Goodreads: ✅ Link available")

# Test genre inference
print("\n" + "=" * 70)
print("GENRE INFERENCE TEST")
print("=" * 70)

if hasattr(recommender, 'book_idx_to_kmeans_cluster'):
    # Check a book without original metadata
    for book_idx in range(min(50, recommender.get_book_count())):
        quality = recommender.metadata_quality.get(book_idx, 'missing')
        if quality in ['missing', 'partial']:
            meta = recommender.get_book_meta(book_idx)
            print(f"\n📖 Book #{book_idx}: {meta['title'][:50]}")
            print(f"   Original quality: {quality}")
            print(f"   Inferred genre: {meta['genre']}")
            break

print("\n" + "=" * 70)
print("✅ All tests completed!")
print("=" * 70)
print("\nYou should now see:")
print("  • Colorful placeholder covers instead of gray boxes")
print("  • Inferred genres from collaborative clusters")
print("  • Quality badges (⚙️ Inferred or ⚠️ Partial)")
print("  • Goodreads search links for all books")
