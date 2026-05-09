"""
Test script untuk AI Sentiment Analysis.
Jalankan: python test_sentiment.py
"""

from src.analysis.sentiment import TruthEngineAI


def test_sentiment():
    print("=" * 60)
    print("🧠 TESTING AI SENTIMENT ANALYSIS")
    print("=" * 60)

    # Load model (ini bisa download model pertama kali dan butuh waktu)
    analyzer = TruthEngineAI()

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

        result = analyzer.analyze(item["text"], source_credibility=0.8)

        if result:
            print(f"   Label: {result['sentiment_label']}")
            print(f"   Confidence: {result['confidence']:.2%}")
            print(f"   Noise Probability: {result['noise_probability']:.2%}")
            print(f"   Integrity Score: {result['integrity_score']:.3f}")

    print("\n" + "=" * 60)
    print("✅ AI SENTIMENT ANALYSIS TEST COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    test_sentiment()
