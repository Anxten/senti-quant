"""
Test script untuk AI Sentiment Analysis.
Jalankan: python test_sentiment.py
"""

from src.analysis.sentiment import get_analyzer

def test_sentiment():
    print("=" * 60)
    print("🧠 TESTING AI SENTIMENT ANALYSIS")
    print("=" * 60)
    
    # Load model (ini akan download model pertama kali, ~400MB)
    analyzer = get_analyzer()
    
    # Test cases: berita finansial
    test_texts = [
        {
            "title": "Positive News",
            "text": "Stock market reaches all-time high as investors show strong confidence in economic recovery. Major tech companies report record profits."
        },
        {
            "title": "Negative News",
            "text": "Market crashes amid fears of recession. Investors panic as unemployment rates surge and companies announce massive layoffs."
        },
        {
            "title": "Neutral News",
            "text": "The central bank maintains interest rates at current levels. Analysts expect steady economic growth in the coming quarter."
        }
    ]
    
    print("\n📊 ANALYZING TEST ARTICLES:\n")
    
    for i, item in enumerate(test_texts, 1):
        print(f"\n{i}. {item['title']}")
        print("-" * 60)
        
        # Basic analysis
        result = analyzer.analyze(item['text'])
        
        if result:
            print(f"   Label: {result['label'].upper()}")
            print(f"   Confidence: {result['confidence']:.2%}")
            print(f"   Sentiment Score: {result['sentiment_score']:.3f}")
        
        # Analysis with integrity (Truth Engine)
        result_integrity = analyzer.analyze_with_integrity(
            item['text'],
            source_credibility=0.8,  # Assume trusted source
            noise_probability=0.1     # 10% noise
        )
        
        if result_integrity:
            print(f"   Integrity Score: {result_integrity['integrity_score']:.3f}")
    
    print("\n" + "=" * 60)
    print("✅ AI SENTIMENT ANALYSIS TEST COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    test_sentiment()
