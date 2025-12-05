#!/usr/bin/env python3
"""
Test backward compatibility of bedrock_converse.py
Tests both text-only and multimodal scenarios
"""

import os
import sys
import json

# Add nova-prompt-optimizer to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'nova-prompt-optimizer', 'src'))

# Disable proxy for direct Bedrock access
if 'BEDROCK_PROXY_ENDPOINT' in os.environ:
    del os.environ['BEDROCK_PROXY_ENDPOINT']
if 'BEDROCK_PROXY_API_KEY' in os.environ:
    del os.environ['BEDROCK_PROXY_API_KEY']

from amzn_nova_prompt_optimizer.core.inference.adapter import BedrockInferenceAdapter

def get_default_config():
    """Get default inference config"""
    return {
        "max_tokens": 200,
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 50
    }

def test_text_only():
    """Test 1: Pure text prompt (original behavior)"""
    print("\n" + "="*80)
    print("TEST 1: Text-only prompt (backward compatibility)")
    print("="*80)
    
    inference_adapter = BedrockInferenceAdapter(region_name="us-west-2")
    
    try:
        result = inference_adapter.call_model(
            model_id="us.amazon.nova-lite-v1:0",
            system_prompt="You are a helpful assistant.",
            messages=[{"user": "What is 2+2?"}],
            inf_config=get_default_config()
        )
        print(f"✅ Text-only test PASSED")
        print(f"Response: {result[:200]}")
        return True
    except Exception as e:
        print(f"❌ Text-only test FAILED: {e}")
        return False


def test_text_with_template_variable():
    """Test 2: Text with template variables (should not try to load image)"""
    print("\n" + "="*80)
    print("TEST 2: Template variable (should not load image)")
    print("="*80)
    
    inference_adapter = BedrockInferenceAdapter(region_name="us-west-2")
    
    try:
        result = inference_adapter.call_model(
            model_id="us.amazon.nova-lite-v1:0",
            system_prompt="You are a helpful assistant.",
            messages=[{"user": "Analyze this image for watermarks: {input}"}],
            inf_config=get_default_config()
        )
        print(f"✅ Template variable test PASSED")
        print(f"Response: {result[:200]}")
        return True
    except Exception as e:
        print(f"❌ Template variable test FAILED: {e}")
        return False


def test_multimodal_with_image():
    """Test 3: Multimodal prompt with actual image"""
    print("\n" + "="*80)
    print("TEST 3: Multimodal with image")
    print("="*80)
    
    # Check if test image exists
    test_image = "images/image_0000.jpg"
    if not os.path.exists(test_image):
        print(f"⚠️  Test image not found: {test_image}")
        print("Creating a test image...")
        os.makedirs("images", exist_ok=True)
        # Create a simple test image
        try:
            from PIL import Image
            img = Image.new('RGB', (100, 100), color='red')
            img.save(test_image)
            print(f"✓ Created test image: {test_image}")
        except ImportError:
            print("❌ PIL not available, skipping multimodal test")
            return None
    
    inference_adapter = BedrockInferenceAdapter(region_name="us-west-2")
    
    try:
        result = inference_adapter.call_model(
            model_id="us.amazon.nova-lite-v1:0",
            system_prompt="You are a helpful assistant that analyzes images.",
            messages=[{"user": f"Analyze this image for watermarks: {test_image}"}],
            inf_config=get_default_config()
        )
        print(f"✅ Multimodal test PASSED")
        print(f"Response: {result[:200]}")
        return True
    except Exception as e:
        print(f"❌ Multimodal test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_conversation_history():
    """Test 4: Multi-turn conversation (original behavior)"""
    print("\n" + "="*80)
    print("TEST 4: Multi-turn conversation")
    print("="*80)
    
    inference_adapter = BedrockInferenceAdapter(region_name="us-west-2")
    
    try:
        result = inference_adapter.call_model(
            model_id="us.amazon.nova-lite-v1:0",
            system_prompt="You are a helpful assistant.",
            messages=[
                {"user": "My name is Alice"},
                {"assistant": "Hello Alice! Nice to meet you."},
                {"user": "What is my name?"}
            ],
            inf_config=get_default_config()
        )
        print(f"✅ Conversation test PASSED")
        print(f"Response: {result[:200]}")
        # Check if it remembers the name
        if "alice" in result.lower():
            print("✓ Correctly remembered conversation context")
        return True
    except Exception as e:
        print(f"❌ Conversation test FAILED: {e}")
        return False


def test_miprov2_format():
    """Test 5: MIPROv2 format with brackets"""
    print("\n" + "="*80)
    print("TEST 5: MIPROv2 format ([][path])")
    print("="*80)
    
    # Check if test image exists
    test_image = "images/image_0000.jpg"
    if not os.path.exists(test_image):
        print(f"⚠️  Test image not found, skipping")
        return None
    
    inference_adapter = BedrockInferenceAdapter(region_name="us-west-2")
    
    try:
        # MIPROv2 format: [][actual_path]
        result = inference_adapter.call_model(
            model_id="us.amazon.nova-lite-v1:0",
            system_prompt="You are a helpful assistant that analyzes images.",
            messages=[{"user": f"Analyze this image for watermarks: [][{test_image}]"}],
            inf_config=get_default_config()
        )
        print(f"✅ MIPROv2 format test PASSED")
        print(f"Response: {result[:200]}")
        return True
    except Exception as e:
        print(f"❌ MIPROv2 format test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_image_support_disabled():
    """Test 6: Image support explicitly disabled"""
    print("\n" + "="*80)
    print("TEST 6: Image support disabled")
    print("="*80)
    
    from amzn_nova_prompt_optimizer.core.inference.bedrock_converse import BedrockConverseHandler
    import boto3
    
    try:
        session = boto3.Session()
        bedrock_client = session.client('bedrock-runtime', region_name='us-west-2')
        
        # Create handler with image support disabled
        handler = BedrockConverseHandler(bedrock_client, enable_image_support=False)
        
        # Try to use image path (should treat as text)
        messages = handler._get_messages([{"user": "Analyze this image for watermarks: images/test.jpg"}])
        
        # Should have text content, not image
        content = messages[0]['content']
        has_text = any('text' in block for block in content)
        has_image = any('image' in block for block in content)
        
        if has_text and not has_image:
            print(f"✅ Image support disabled test PASSED")
            print(f"Content treated as text: {content}")
            return True
        else:
            print(f"❌ Image support disabled test FAILED")
            print(f"Expected text only, got: {content}")
            return False
    except Exception as e:
        print(f"❌ Image support disabled test FAILED: {e}")
        return False


def main():
    print("\n" + "="*80)
    print("BEDROCK CONVERSE COMPATIBILITY TEST SUITE")
    print("="*80)
    
    results = {
        "Text-only": test_text_only(),
        "Template variable": test_text_with_template_variable(),
        "Multimodal": test_multimodal_with_image(),
        "Conversation": test_conversation_history(),
        "MIPROv2 format": test_miprov2_format(),
        "Image disabled": test_image_support_disabled()
    }
    
    print("\n" + "="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result is True else "❌ FAIL" if result is False else "⚠️  SKIP"
        print(f"{test_name:20s}: {status}")
    
    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed > 0:
        print("\n❌ Some tests failed!")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
