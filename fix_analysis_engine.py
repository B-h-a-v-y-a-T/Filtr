"""
Script to fix analysis_engine.py by removing all publishers/published_dates references
and fixing duplicate source additions.
"""
import re

file_path = r'c:\Users\bhavy\OneDrive\Desktop\Hackathons\Filtr_Working_Without_Logs\backend\app\services\analysis_engine.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove duplicate source additions in misinformation fallback (lines ~916-919)
content = re.sub(
    r'(\s+url = fc_claim\.get\("url", ""\))\s+if url and url not in sources:\s+sources\.append\(url\)\s+if publisher and publisher not in publishers:\s+publishers\.append\(publisher\)',
    r'\1',
    content
)

# Remove all standalone publishers.append lines
content = re.sub(r'\s+if publisher and publisher not in publishers:\s+publishers\.append\(publisher\)', '', content)
content = re.sub(r'\s+if article\.get\("source"\) and article\.get\("source"\) not in publishers:\s+publishers\.append\(article\.get\("source"\)\)', '', content)

# Remove all standalone published_dates.append lines  
content = re.sub(r'\s+if pub_date:\s+published_dates\.append\(pub_date\)', '', content)
content = re.sub(r'\s+if claim_date:\s+published_dates\.append\(claim_date\)', '', content)

# Remove "publisher": publishers[:10] from return statements
content = re.sub(r',\s+"publisher": publishers\[:10\]', '', content)

# Remove "published_dates": published_dates[:10] from return statements
content = re.sub(r',\s+"published_dates": published_dates\[:10\]', '', content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed analysis_engine.py successfully!")
print("- Removed duplicate source additions")
print("- Removed all publishers.append references")
print("- Removed all published_dates.append references")
print("- Removed publishers/published_dates from return statements")
