#!/usr/bin/env python3
"""
Phase 1 Test Script
Test multi-provider LLM and document parsing functionality
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_providers():
    """Test LLM provider initialization."""
    print("\n" + "=" * 60)
    print("TEST 1: LLM Provider Initialization")
    print("=" * 60)

    from llm.providers import ProviderFactory
    from config import ANTHROPIC_API_KEY, OPENAI_API_KEY

    # Test Anthropic
    if ANTHROPIC_API_KEY and ANTHROPIC_API_KEY != "VOTRE_CLE_API_ICI":
        try:
            anthropic = ProviderFactory.create("anthropic", api_key=ANTHROPIC_API_KEY)
            print(f"✓ Anthropic provider initialized")
            print(f"  - Name: {anthropic.name}")
            print(f"  - Supports vision: {anthropic.supports_vision()}")
        except Exception as e:
            print(f"✗ Anthropic provider failed: {e}")
    else:
        print("⊘ Anthropic API key not configured")

    # Test OpenAI
    if OPENAI_API_KEY:
        try:
            openai = ProviderFactory.create("openai", api_key=OPENAI_API_KEY)
            print(f"✓ OpenAI provider initialized")
            print(f"  - Name: {openai.name}")
            print(f"  - Supports vision: {openai.supports_vision()}")
        except Exception as e:
            print(f"✗ OpenAI provider failed: {e}")
    else:
        print("⊘ OpenAI API key not configured")

    # Test Ollama
    try:
        ollama = ProviderFactory.create("ollama")
        if ollama.available:
            print(f"✓ Ollama provider initialized")
            print(f"  - Name: {ollama.name}")
            print(f"  - Base URL: {ollama.base_url}")
        else:
            print("⊘ Ollama not available (server not running)")
    except Exception as e:
        print(f"⊘ Ollama not available: {e}")


def test_document_parser():
    """Test document parsing."""
    print("\n" + "=" * 60)
    print("TEST 2: Document Parser")
    print("=" * 60)

    from document.parser import DocumentParser

    parser = DocumentParser(use_vision=False)  # Disable vision for basic test

    # Test with existing rfp.md file
    rfp_path = os.path.join(os.path.dirname(__file__), "rfp.md")

    if os.path.exists(rfp_path):
        try:
            doc = parser.parse(rfp_path)
            print(f"✓ Parsed document: {doc.file_path}")
            print(f"  - Text length: {len(doc.text)} characters")
            print(f"  - Sections found: {len(doc.sections)}")
            if doc.sections:
                print(f"  - First section: {doc.sections[0].title}")
            print(f"  - Metadata: {doc.metadata}")
        except Exception as e:
            print(f"✗ Document parsing failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"⊘ Test file not found: {rfp_path}")


def test_model_router():
    """Test model router."""
    print("\n" + "=" * 60)
    print("TEST 3: Model Router")
    print("=" * 60)

    from llm.providers import ProviderFactory, LLMRequest
    from llm.router import ModelRouter, CostTracker
    from config import ANTHROPIC_API_KEY

    if not ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == "VOTRE_CLE_API_ICI":
        print("⊘ Skipped (no API key configured)")
        return

    try:
        # Create providers
        providers = {
            "anthropic": ProviderFactory.create("anthropic", api_key=ANTHROPIC_API_KEY)
        }

        # Create router with budget
        cost_tracker = CostTracker(budget_limit=1.0)  # $1 budget
        router = ModelRouter(providers=providers, cost_tracker=cost_tracker)

        print(f"✓ Model router initialized")
        print(f"  - Available providers: {list(providers.keys())}")
        print(f"  - Budget limit: ${cost_tracker.budget_limit:.2f}")

        # Test routing config
        router.update_routing_config("TEST", "simple", "claude-haiku-4-5-20251001")
        print(f"✓ Routing config updated")

        # Get cost summary
        summary = router.get_cost_summary()
        print(f"  - Total cost: ${summary['total_cost']:.4f}")
        print(f"  - Remaining budget: ${summary['remaining']:.2f}")

    except Exception as e:
        print(f"✗ Model router test failed: {e}")
        import traceback
        traceback.print_exc()


def test_llm_client_integration():
    """Test integrated LLM client with multi-provider support."""
    print("\n" + "=" * 60)
    print("TEST 4: LLM Client Integration")
    print("=" * 60)

    from agents import LLMClient

    try:
        client = LLMClient()

        if client.use_multi_provider:
            print(f"✓ Multi-provider mode active")
            print(f"  - Providers available: {list(client.router.providers.keys())}")
            print(f"  - Budget limit: ${client.cost_tracker.budget_limit:.2f}")

            # Test a simple call (if not in simulation mode)
            if not client.simulation:
                print("\n  Testing simple LLM call...")
                response = client.call(
                    agent_name="TEST",
                    system_prompt="You are a test assistant.",
                    user_message="Say 'Hello, Phase 1 working!' in exactly 5 words.",
                    task_type="simple"
                )
                print(f"  Response: {response[:100]}...")

                # Get cost summary
                summary = client.get_cost_summary()
                print(f"  Cost: ${summary['total_cost']:.4f}")
        else:
            print(f"⊘ Running in legacy mode")
            if client.simulation:
                print(f"  - Simulation mode active")
            else:
                print(f"  - Using Anthropic-only client")

    except Exception as e:
        print(f"✗ LLM client test failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all Phase 1 tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  KPLW Phase 1 Test Suite".center(58) + "║")
    print("║" + "  Multi-Provider LLM + Document Parsing".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")

    test_providers()
    test_document_parser()
    test_model_router()
    test_llm_client_integration()

    print("\n" + "=" * 60)
    print("Phase 1 Testing Complete")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Configure .env file with API keys")
    print("3. Run full workflow test: python main.py --demo")
    print()


if __name__ == "__main__":
    main()
