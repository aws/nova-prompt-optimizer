#!/bin/bash
set -e

echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info src/*.egg-info

echo "🔨 Building package..."
python3 -m build

echo ""
echo "✅ Build complete!"
echo ""
echo "📦 Generated files:"
ls -lh dist/

echo ""
echo "🚀 To install locally:"
echo "   pip install dist/nova_prompt_optimizer-*-py3-none-any.whl"
echo ""
echo "📤 To distribute:"
echo "   - Share the .whl file directly"
echo "   - Upload to internal PyPI: twine upload --repository-url <url> dist/*"
echo "   - Upload to S3: aws s3 cp dist/*.whl s3://your-bucket/packages/"
echo "   - Attach to GitHub release"
