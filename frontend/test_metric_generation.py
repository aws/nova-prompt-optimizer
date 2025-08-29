#!/usr/bin/env python3
from database import Database
from services.metric_service import MetricService

# Get the current metric from database
db = Database()
metric = db.get_metric_by_id('metric_dadd8760')
print('Current metric code length:', len(metric['generated_code']))
print('Current metric preview:', metric['generated_code'][:200])
print()

# Test generating new composite metric code
test_metrics = [
    {'name': 'Test Metric 1', 'description': 'Test description 1', 'type': 'accuracy', 'complexity': 'simple'},
    {'name': 'Test Metric 2', 'description': 'Test description 2', 'type': 'similarity', 'complexity': 'moderate'}
]

try:
    service = MetricService()
    print('Generating new composite metric code...')
    new_code = service.generate_composite_metric_code(test_metrics)
    print('New generated code length:', len(new_code))
    print('New code preview:', new_code[:300])
    
    if len(new_code) > 1000:
        print('✅ Success! Generated proper composite metric code')
        # Update the database
        db.update_metric_code('metric_dadd8760', new_code)
        print('✅ Database updated with new code')
    else:
        print('❌ Still getting fallback code - need to debug further')
        
except Exception as e:
    print('❌ Error:', str(e))
    import traceback
    traceback.print_exc()