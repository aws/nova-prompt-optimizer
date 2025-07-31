# Troubleshooting Guide

This guide helps you resolve common issues when using the Nova Prompt Optimizer Frontend.

## General Issues

### Application Won't Load

#### Symptoms
- Blank page or loading spinner that never completes
- Error messages about network connectivity
- Browser console shows JavaScript errors

#### Solutions
1. **Check Internet Connection**
   - Verify you can access other websites
   - Try refreshing the page (Ctrl+F5 or Cmd+Shift+R)

2. **Browser Compatibility**
   - Use a modern browser (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
   - Enable JavaScript if disabled
   - Clear browser cache and cookies

3. **Network/Firewall Issues**
   - Check if your organization blocks certain domains
   - Try accessing from a different network
   - Contact IT support if behind corporate firewall

4. **Server Issues**
   - Check if the service is experiencing downtime
   - Try again in a few minutes
   - Contact system administrator

### Slow Performance

#### Symptoms
- Pages take a long time to load
- Interactions feel sluggish
- File uploads timeout

#### Solutions
1. **Browser Optimization**
   - Close unnecessary browser tabs
   - Disable browser extensions temporarily
   - Try incognito/private browsing mode

2. **Network Issues**
   - Check internet speed (minimum 10 Mbps recommended)
   - Try wired connection instead of WiFi
   - Avoid peak usage times

3. **System Resources**
   - Close other applications to free memory
   - Restart browser if it's been running long
   - Check available disk space

## Dataset Issues

### Upload Failures

#### File Format Errors
**Error**: "Unsupported file format"
**Solutions**:
- Ensure file is CSV or JSON format
- Check file extension (.csv, .json, .jsonl)
- Verify file isn't corrupted
- Try saving in a different format

#### File Size Errors
**Error**: "File too large"
**Solutions**:
- Check file size limit (usually 100MB)
- Compress or split large files
- Remove unnecessary columns or rows
- Use more efficient file formats

#### Encoding Issues
**Error**: "Unable to parse file" or garbled text
**Solutions**:
- Save file with UTF-8 encoding
- Remove special characters if possible
- Try different text editor for saving
- Check for byte order marks (BOM)

### Data Processing Errors

#### Column Mapping Issues
**Error**: "Required columns not found"
**Solutions**:
- Verify column names match exactly (case-sensitive)
- Check for extra spaces in column names
- Ensure input/output columns exist in data
- Review column mapping selections

#### Data Quality Problems
**Error**: "Invalid data format" or "Missing values"
**Solutions**:
- Remove or fill missing values
- Ensure consistent data types within columns
- Check for malformed JSON objects
- Validate CSV structure (equal columns per row)

#### Memory Issues
**Error**: "Out of memory" or browser crashes
**Solutions**:
- Reduce dataset size for testing
- Split large datasets into smaller chunks
- Close other browser tabs
- Try on a machine with more RAM

## Prompt Issues

### Variable Detection Problems

#### Variables Not Recognized
**Symptoms**: Variables don't appear in the detected variables list
**Solutions**:
- Use correct syntax: `{{variable_name}}`
- Avoid spaces in variable names
- Check for typos in variable syntax
- Ensure variables are in the prompt text, not comments

#### Variable Mismatch
**Error**: "Variable not found in dataset"
**Solutions**:
- Ensure variable names exactly match dataset columns
- Check case sensitivity ({{Input}} vs {{input}})
- Verify column names don't have extra spaces
- Review dataset column mapping

### Template Rendering Issues

#### Preview Doesn't Work
**Symptoms**: Preview shows errors or empty content
**Solutions**:
- Check Jinja2 template syntax
- Ensure all variables are properly closed
- Test with simple variables first
- Review template logic for errors

#### Syntax Errors
**Error**: "Template syntax error"
**Solutions**:
- Check for unmatched braces `{{ }}`
- Verify proper Jinja2 syntax
- Remove complex logic from templates
- Test templates incrementally

## Optimization Issues

### Configuration Problems

#### Missing Components
**Error**: "Please select dataset/prompt/metric"
**Solutions**:
- Ensure all required components are selected
- Verify components are properly saved
- Check that dataset processing completed
- Refresh page and try again

#### Parameter Validation
**Error**: "Invalid optimization parameters"
**Solutions**:
- Check parameter ranges (iterations, population size)
- Ensure numeric values are within limits
- Verify model selection is valid
- Review advanced parameter settings

### Runtime Errors

#### Optimization Fails to Start
**Symptoms**: Error immediately after clicking "Start"
**Solutions**:
- Check AWS credentials and permissions
- Verify model availability in your region
- Ensure sufficient API quotas
- Try with smaller dataset first

#### Optimization Stops Unexpectedly
**Symptoms**: Progress stops, error messages in logs
**Solutions**:
- Check optimization logs for specific errors
- Verify network connectivity remains stable
- Ensure sufficient system resources
- Try restarting with different parameters

#### No Improvement in Results
**Symptoms**: Optimized prompt performs same as original
**Solutions**:
- Increase iteration count
- Try different optimizer
- Review metric selection and implementation
- Check if original prompt is already optimal

### Performance Issues

#### Very Slow Optimization
**Symptoms**: Optimization takes much longer than expected
**Solutions**:
- Reduce dataset size for testing
- Lower iteration count or population size
- Try faster model (Nova Lite vs Nova Pro)
- Optimize custom metrics for speed

#### High API Costs
**Symptoms**: Unexpected charges from AWS
**Solutions**:
- Monitor API usage during optimization
- Use smaller datasets for experimentation
- Set evaluation budgets in advanced settings
- Consider using Nova Lite for development

## Custom Metrics Issues

### Code Errors

#### Syntax Errors
**Error**: "Python syntax error"
**Solutions**:
- Check Python syntax carefully
- Ensure proper indentation (use spaces, not tabs)
- Verify all parentheses and brackets are matched
- Test code in external Python environment first

#### Runtime Errors
**Error**: "Metric execution failed"
**Solutions**:
- Add error handling for edge cases
- Check for division by zero
- Handle empty strings and None values
- Add input validation

#### Import Errors
**Error**: "Module not found"
**Solutions**:
- Use only standard Python libraries
- Avoid external dependencies
- Check spelling of import statements
- Use built-in functions when possible

### Logic Issues

#### Incorrect Scores
**Symptoms**: Metric returns unexpected values
**Solutions**:
- Test with known examples
- Add debug print statements
- Verify scoring scale (0.0 to 1.0)
- Check edge case handling

#### Performance Problems
**Symptoms**: Metric evaluation is very slow
**Solutions**:
- Optimize expensive operations
- Use batch processing when possible
- Cache repeated computations
- Simplify complex logic

## Annotation Issues

### Rubric Generation Problems

#### AI Generation Fails
**Error**: "Unable to generate rubric"
**Solutions**:
- Check dataset quality and size
- Ensure ground truth data is meaningful
- Try with different dataset samples
- Review AWS model availability

#### Poor Quality Rubrics
**Symptoms**: Generated rubrics don't make sense
**Solutions**:
- Improve dataset quality and consistency
- Provide more diverse examples
- Edit rubric manually after generation
- Try different generation parameters

### Annotation Workflow Issues

#### Task Assignment Problems
**Symptoms**: Annotators can't see their tasks
**Solutions**:
- Verify user permissions and roles
- Check task assignment configuration
- Ensure annotation tasks were created properly
- Refresh browser and try again

#### Agreement Calculation Errors
**Error**: "Unable to calculate agreement"
**Solutions**:
- Ensure multiple annotators completed same tasks
- Check for consistent annotation formats
- Verify all required annotations are submitted
- Review agreement calculation settings

## Browser-Specific Issues

### Chrome
- **File Upload Issues**: Try disabling extensions
- **Memory Problems**: Enable "Memory Saver" mode
- **CORS Errors**: Check site permissions

### Firefox
- **Slow Performance**: Disable tracking protection temporarily
- **Upload Failures**: Check file handling preferences
- **Display Issues**: Try refreshing with Ctrl+Shift+R

### Safari
- **JavaScript Errors**: Enable "Develop" menu and check console
- **File Handling**: Check download preferences
- **Compatibility**: Ensure Safari 14+ for full functionality

### Edge
- **Legacy Issues**: Ensure using Chromium-based Edge
- **Security Warnings**: Add site to trusted sites if needed
- **Performance**: Clear browsing data regularly

## Error Messages Reference

### Common Error Codes

#### HTTP 400 - Bad Request
**Meaning**: Invalid request data
**Solutions**:
- Check form inputs for errors
- Verify file format and size
- Review parameter values
- Try refreshing and submitting again

#### HTTP 401 - Unauthorized
**Meaning**: Authentication required or expired
**Solutions**:
- Log in again if session expired
- Check user permissions
- Contact administrator for access
- Clear cookies and log in fresh

#### HTTP 403 - Forbidden
**Meaning**: Access denied
**Solutions**:
- Verify user has required permissions
- Check if feature is enabled for your account
- Contact administrator
- Try different user account

#### HTTP 404 - Not Found
**Meaning**: Resource doesn't exist
**Solutions**:
- Check URL for typos
- Verify resource wasn't deleted
- Try navigating from main page
- Contact support if persistent

#### HTTP 500 - Internal Server Error
**Meaning**: Server-side error
**Solutions**:
- Try again in a few minutes
- Check if issue persists
- Contact system administrator
- Report error with details

### Application-Specific Errors

#### "Dataset processing failed"
- Check file format and encoding
- Verify column mapping is correct
- Ensure data quality meets requirements
- Try with smaller sample first

#### "Optimization timeout"
- Reduce dataset size or iterations
- Check network connectivity
- Try during off-peak hours
- Contact administrator about resource limits

#### "Metric evaluation error"
- Review custom metric code
- Test metric with sample data
- Check for runtime errors
- Simplify metric logic

## Getting Additional Help

### Before Contacting Support

1. **Gather Information**
   - Note exact error messages
   - Record steps to reproduce issue
   - Check browser console for errors
   - Note your browser and OS version

2. **Try Basic Solutions**
   - Refresh the page
   - Clear browser cache
   - Try different browser
   - Check internet connection

3. **Document the Issue**
   - Screenshot error messages
   - Note when issue started
   - List what you were trying to do
   - Include any relevant file names or IDs

### Support Channels

#### System Administrator
- For access and permission issues
- Server downtime or performance problems
- Account setup and configuration
- Resource limit increases

#### Technical Support
- For application bugs and errors
- Feature questions and guidance
- Integration and API issues
- Performance optimization help

#### User Community
- For best practices and tips
- Sharing solutions to common problems
- Feature requests and feedback
- Learning from other users' experiences

### Self-Help Resources

#### Documentation
- Review relevant user guide sections
- Check API documentation for technical details
- Look for similar issues in troubleshooting
- Read release notes for known issues

#### Testing Environment
- Try reproducing issue with sample data
- Test in different browser or incognito mode
- Use smaller datasets to isolate problems
- Compare with working examples

Remember: Most issues have simple solutions. Start with the basics (refresh, clear cache, check network) before diving into complex troubleshooting.