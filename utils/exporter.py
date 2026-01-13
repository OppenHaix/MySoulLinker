import pandas as pd
from datetime import datetime
import os
import json
import zipfile
from io import BytesIO

def export_chat_logs_to_excel(chat_logs, contact_name, include_analysis=False):
    data = []
    for log in chat_logs:
        row = {
            '日期': log.chat_date.strftime('%Y-%m-%d') if log.chat_date else '',
            '发言者': log.speaker,
            '内容': log.content
        }
        if include_analysis:
            row['分析备注'] = ''
        data.append(row)
    
    df = pd.DataFrame(data)
    
    filename = f"聊天记录_{contact_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    filepath = os.path.join('exports', filename)
    
    os.makedirs('exports', exist_ok=True)
    
    df.to_excel(filepath, index=False, engine='openpyxl')
    
    return filepath, filename

def export_chat_logs_to_csv(chat_logs, contact_name):
    data = []
    for log in chat_logs:
        data.append({
            '日期': log.chat_date.strftime('%Y-%m-%d') if log.chat_date else '',
            '发言者': log.speaker,
            '内容': log.content
        })
    
    df = pd.DataFrame(data)
    
    filename = f"聊天记录_{contact_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join('exports', filename)
    
    os.makedirs('exports', exist_ok=True)
    
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    
    return filepath, filename

def export_chat_logs_to_multiple_formats(chat_logs, contact_name, formats, include_analysis=False):
    buffer = BytesIO()
    
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        if 'xlsx' in formats:
            filepath, _ = export_chat_logs_to_excel(chat_logs, contact_name, include_analysis)
            with open(filepath, 'rb') as f:
                zf.writestr(f"聊天记录_{contact_name}.xlsx", f.read())
            os.remove(filepath)
        
        if 'csv' in formats:
            filepath, _ = export_chat_logs_to_csv(chat_logs, contact_name)
            with open(filepath, 'rb') as f:
                zf.writestr(f"聊天记录_{contact_name}.csv", f.read())
            os.remove(filepath)
    
    filename = f"聊天记录_{contact_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    filepath = os.path.join('exports', filename)
    
    os.makedirs('exports', exist_ok=True)
    
    with open(filepath, 'wb') as f:
        f.write(buffer.getvalue())
    
    return filepath, filename

def export_analysis_to_excel(analysis, contact_name, include_personality=True, include_interests=True, include_guide=True):
    parsed_data = analysis.get_parsed_data()
    
    filename = f"分析报告_{contact_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    filepath = os.path.join('exports', filename)
    
    os.makedirs('exports', exist_ok=True)
    
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        summary_df = pd.DataFrame([{
            '联系人': contact_name,
            '分析摘要': parsed_data.get('summary', ''),
            '创建时间': analysis.created_at.strftime('%Y-%m-%d %H:%M:%S') if analysis.created_at else ''
        }])
        summary_df.to_excel(writer, sheet_name='摘要', index=False)
        
        if include_interests and 'interests' in parsed_data:
            interests_df = pd.DataFrame({
                '关键词': parsed_data['interests']
            })
            interests_df.to_excel(writer, sheet_name='兴趣关键词', index=False)
        
        if include_personality:
            traits_data = []
            for dimension, fields in [
                ('核心特质', 'core_traits'),
                ('行为偏好', 'behavior_preferences'),
                ('社交互动', 'social_interaction'),
                ('认知思维', 'cognitive_thinking')
            ]:
                if fields in parsed_data:
                    for key, value in parsed_data[fields].items():
                        traits_data.append({
                            '维度': dimension,
                            '特质': key,
                            '描述': str(value)
                        })
            
            if traits_data:
                traits_df = pd.DataFrame(traits_data)
                traits_df.to_excel(writer, sheet_name='性格特质', index=False)
        
        if include_guide and 'dos_and_donts' in parsed_data:
            dos_donts_data = []
            for item in parsed_data['dos_and_donts'].get('dos', []):
                dos_donts_data.append({'类型': '应该做', '事项': item})
            for item in parsed_data['dos_and_donts'].get('donts', []):
                dos_donts_data.append({'类型': '不应该做', '事项': item})
            
            if dos_donts_data:
                dos_donts_df = pd.DataFrame(dos_donts_data)
                dos_donts_df.to_excel(writer, sheet_name='相处指南', index=False)
    
    return filepath, filename

def export_analysis_to_json(analysis, contact_name):
    parsed_data = analysis.get_parsed_data()
    
    export_data = {
        'contact_name': contact_name,
        'summary': parsed_data.get('summary', ''),
        'interests': parsed_data.get('interests', []),
        'core_traits': parsed_data.get('core_traits', {}),
        'behavior_preferences': parsed_data.get('behavior_preferences', {}),
        'social_interaction': parsed_data.get('social_interaction', {}),
        'cognitive_thinking': parsed_data.get('cognitive_thinking', {}),
        'dos_and_donts': parsed_data.get('dos_and_donts', {}),
        'created_at': analysis.created_at.strftime('%Y-%m-%d %H:%M:%S') if analysis.created_at else ''
    }
    
    filename = f"分析报告_{contact_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join('exports', filename)
    
    os.makedirs('exports', exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    return filepath, filename

def export_analysis_to_pdf(analysis, contact_name):
    parsed_data = analysis.get_parsed_data()
    
    content = f"""
    分析报告 - {contact_name}
    {'=' * 50}
    
    分析摘要
    {'-' * 30}
    {parsed_data.get('summary', '')}
    
    兴趣关键词
    {'-' * 30}
    {', '.join(parsed_data.get('interests', []))}
    
    性格特质
    {'-' * 30}
    """
    
    for dimension, fields in [
        ('核心特质', 'core_traits'),
        ('行为偏好', 'behavior_preferences'),
        ('社交互动', 'social_interaction'),
        ('认知思维', 'cognitive_thinking')
    ]:
        if fields in parsed_data:
            content += f"\n{dimension}:\n"
            for key, value in parsed_data[fields].items():
                content += f"  - {key}: {value}\n"
    
    if 'dos_and_donts' in parsed_data:
        content += f"\n相处指南\n{'-' * 30}\n"
        content += "应该做:\n"
        for item in parsed_data['dos_and_donts'].get('dos', []):
            content += f"  + {item}\n"
        content += "不应该做:\n"
        for item in parsed_data['dos_and_donts'].get('donts', []):
            content += f"  - {item}\n"
    
    filename = f"分析报告_{contact_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = os.path.join('exports', filename)
    
    os.makedirs('exports', exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filepath, filename

def export_analysis_to_multiple_formats(analysis, contact_name, formats, **kwargs):
    buffer = BytesIO()
    
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        if 'xlsx' in formats:
            filepath, _ = export_analysis_to_excel(analysis, contact_name, **kwargs)
            with open(filepath, 'rb') as f:
                zf.writestr(f"分析报告_{contact_name}.xlsx", f.read())
            os.remove(filepath)
        
        if 'json' in formats:
            filepath, _ = export_analysis_to_json(analysis, contact_name)
            with open(filepath, 'rb') as f:
                zf.writestr(f"分析报告_{contact_name}.json", f.read())
            os.remove(filepath)
        
        if 'pdf' in formats:
            filepath, _ = export_analysis_to_pdf(analysis, contact_name)
            with open(filepath, 'rb') as f:
                zf.writestr(f"分析报告_{contact_name}.txt", f.read())
            os.remove(filepath)
    
    filename = f"分析报告_{contact_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    filepath = os.path.join('exports', filename)
    
    os.makedirs('exports', exist_ok=True)
    
    with open(filepath, 'wb') as f:
        f.write(buffer.getvalue())
    
    return filepath, filename

def generate_summary_report(contact, chat_logs, analysis=None):
    report = {
        'contact_name': contact.name,
        'total_messages': chat_logs.count(),
        'my_messages': chat_logs.filter_by(speaker='我').count(),
        'other_messages': chat_logs.filter_by(speaker='对方').count(),
        'chat_date_range': None
    }
    
    if chat_logs.count() > 0:
        dates = [log.chat_date for log in chat_logs if log.chat_date]
        if dates:
            report['chat_date_range'] = {
                'earliest': min(dates).isoformat(),
                'latest': max(dates).isoformat()
            }
    
    if analysis:
        parsed = analysis.get_parsed_data()
        report['summary'] = parsed.get('summary', '')
        report['interests'] = parsed.get('interests', [])
        report['core_traits'] = parsed.get('core_traits', {})
    
    return report
