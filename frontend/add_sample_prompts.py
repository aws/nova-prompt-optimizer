"""
Add sample prompts with different output formats to test the flexible generator
"""

from database import Database
import uuid
from datetime import datetime

def add_sample_prompts():
    db = Database()
    
    # 1. JSON Format Prompt
    json_prompt = {
        'id': f'prompt_{uuid.uuid4().hex[:8]}',
        'name': 'Customer Feedback Analysis (JSON)',
        'type': 'System + User',
        'variables': {
            'system_prompt': '''You are a customer feedback analysis expert. Analyze customer feedback and return structured data.

OUTPUT FORMAT:
You must respond with valid JSON that follows this exact schema:

```json
{
  "sentiment": "positive|negative|neutral",
  "category": "product|service|billing|technical|other",
  "priority": "high|medium|low",
  "confidence": 0.95,
  "key_issues": ["issue1", "issue2"],
  "recommended_action": "string describing next steps"
}
```

IMPORTANT: 
- Your response must be valid JSON only
- Follow the schema exactly
- Include all required fields
- Use appropriate data types''',
            'user_prompt': '{{ Input }}'
        },
        'created': datetime.now().strftime('%Y-%m-%d'),
        'last_used': datetime.now().isoformat(),
        'performance': 'Not tested'
    }
    
    # 2. Plain Text Format Prompt  
    text_prompt = {
        'id': f'prompt_{uuid.uuid4().hex[:8]}',
        'name': 'Customer Service Chat (Text)',
        'type': 'System + User',
        'variables': {
            'system_prompt': '''You are a friendly customer service representative for a tech company. Help users with their software issues.

RESPONSE REQUIREMENTS:
- Style: Professional but friendly
- Length: 2-4 sentences
- Natural, conversational tone
- Provide helpful solutions

OUTPUT FORMAT:
Respond with plain text only. No special formatting, no JSON, no XML tags.
Just natural conversational text that directly addresses the user's question.
Be empathetic and solution-focused.''',
            'user_prompt': '{{ Input }}'
        },
        'created': datetime.now().strftime('%Y-%m-%d'),
        'last_used': datetime.now().isoformat(),
        'performance': 'Not tested'
    }
    
    # 3. XML Format Prompt (different from existing IT Support)
    xml_prompt = {
        'id': f'prompt_{uuid.uuid4().hex[:8]}',
        'name': 'Product Review Analysis (XML)',
        'type': 'System + User',
        'variables': {
            'system_prompt': '''You are a product review analysis system. Analyze product reviews and extract key information.

OUTPUT FORMAT:
All responses must be formatted in XML as follows:

```xml
<review_analysis>
    <original_review>[Exact user input]</original_review>
    <analysis>
        <rating confidence="[1-10]">[1-5 stars]</rating>
        <sentiment confidence="[1-10]">[positive/negative/neutral]</sentiment>
        <product_category>[electronics/clothing/books/other]</product_category>
        <key_points>
            <pros>[positive aspects mentioned]</pros>
            <cons>[negative aspects mentioned]</cons>
        </key_points>
    </analysis>
    <summary>[Brief summary of the review]</summary>
    <recommendation>
        <helpful_score>[1-10]</helpful_score>
        <reasoning>[Why this score was given]</reasoning>
    </recommendation>
</review_analysis>
```

IMPORTANT: Follow the XML structure exactly as shown.''',
            'user_prompt': '{{ Input }}'
        },
        'created': datetime.now().strftime('%Y-%m-%d'),
        'last_used': datetime.now().isoformat(),
        'performance': 'Not tested'
    }
    
    # Add prompts to database
    try:
        # Create separate database instances for each operation
        db1 = Database()
        db1.create_prompt(
            json_prompt['name'],
            json_prompt['variables']['system_prompt'],
            json_prompt['variables']['user_prompt']
        )
        print(f"✅ Added JSON prompt: {json_prompt['name']}")
        
        db2 = Database()
        db2.create_prompt(
            text_prompt['name'],
            text_prompt['variables']['system_prompt'],
            text_prompt['variables']['user_prompt']
        )
        print(f"✅ Added Text prompt: {text_prompt['name']}")
        
        db3 = Database()
        db3.create_prompt(
            xml_prompt['name'],
            xml_prompt['variables']['system_prompt'],
            xml_prompt['variables']['user_prompt']
        )
        print(f"✅ Added XML prompt: {xml_prompt['name']}")
        
        print("\n🎉 All sample prompts added successfully!")
        print("You can now test the flexible generator with:")
        print("- JSON format (Customer Feedback Analysis)")
        print("- Plain text format (Customer Service Chat)")
        print("- XML format (Product Review Analysis)")
        
    except Exception as e:
        print(f"❌ Error adding prompts: {e}")

if __name__ == "__main__":
    add_sample_prompts()
