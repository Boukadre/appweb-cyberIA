"""
Module 1: Advanced SSH Forensics
Analyzes SSH logs and provides geographic intelligence on attackers
"""

import streamlit as st
import pandas as pd
import requests
import re
from collections import Counter
from typing import List, Dict, Optional
import time


def parse_auth_log(log_content: str) -> List[str]:
    """
    Parse auth.log file and extract IPs with failed authentication attempts
    
    Args:
        log_content: Raw log file content
        
    Returns:
        List of IP addresses with failed attempts
    """
    failed_ips = []
    
    # Multiple patterns to catch different log formats
    patterns = [
        r'Failed password for .* from ([\d\.]+)',
        r'authentication failure.*rhost=([\d\.]+)',
        r'Invalid user .* from ([\d\.]+)',
        r'Failed password for invalid user .* from ([\d\.]+)',
        r'Connection closed by authenticating user .* ([\d\.]+)',
        r'Disconnected from authenticating user .* ([\d\.]+) port \d+ \[preauth\]'
    ]
    
    for line in log_content.split('\n'):
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                ip = match.group(1)
                # Validate IP format
                if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                    failed_ips.append(ip)
                break
    
    return failed_ips


def get_ip_geolocation(ip: str) -> Optional[Dict]:
    """
    Get geolocation data for an IP using ip-api.com (free, no key required)
    
    Args:
        ip: IP address to lookup
        
    Returns:
        Dictionary with geolocation data or None if error
    """
    try:
        url = f"http://ip-api.com/json/{ip}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                return {
                    'ip': ip,
                    'country': data.get('country', 'Unknown'),
                    'countryCode': data.get('countryCode', 'XX'),
                    'city': data.get('city', 'Unknown'),
                    'isp': data.get('isp', 'Unknown'),
                    'lat': data.get('lat', 0.0),
                    'lon': data.get('lon', 0.0),
                    'timezone': data.get('timezone', 'Unknown'),
                    'org': data.get('org', 'Unknown')
                }
            else:
                return None
        else:
            return None
            
    except Exception as e:
        st.error(f"Error fetching geolocation for {ip}: {str(e)}")
        return None


def get_country_flag_emoji(country_code: str) -> str:
    """
    Convert country code to flag emoji
    
    Args:
        country_code: 2-letter country code (e.g., 'US', 'FR')
        
    Returns:
        Flag emoji or empty string
    """
    if len(country_code) != 2:
        return "🏴"
    
    # Convert country code to regional indicator symbols
    flag = ''.join(chr(127397 + ord(c)) for c in country_code.upper())
    return flag


def render_ssh_forensics():
    """Main rendering function for SSH Forensics module"""
    
    st.header("🔒 Advanced SSH Forensics")
    st.markdown("""
    **Analyze SSH authentication logs and discover geographic origins of attacks**
    
    This module provides:
    - Deep parsing of auth.log files
    - Geographic intelligence on attackers (Country, City, ISP)
    - Interactive map visualization
    - Detailed attack statistics
    """)
    
    # File uploader
    uploaded_file = st.file_uploader(
        "📁 Upload SSH Auth Log",
        type=['log', 'txt'],
        help="Upload your /var/log/auth.log or similar SSH authentication log file"
    )
    
    if not uploaded_file:
        st.info("👆 Upload an auth.log file to begin analysis")
        
        # Show example
        with st.expander("📄 Example Log Format"):
            st.code("""Nov 26 08:15:23 server sshd[12345]: Failed password for root from 192.168.1.100 port 22 ssh2
Nov 26 08:16:01 server sshd[12348]: Failed password for invalid user test from 203.0.113.50 port 22 ssh2
Nov 26 08:17:12 server sshd[12352]: authentication failure; rhost=198.51.100.25""")
        return
    
    # Parse the log file
    try:
        log_content = uploaded_file.read().decode('utf-8', errors='ignore')
    except Exception as e:
        st.error(f"❌ Error reading file: {str(e)}")
        return
    
    with st.spinner("🔍 Parsing log file..."):
        failed_ips = parse_auth_log(log_content)
    
    if not failed_ips:
        st.warning("⚠️ No failed authentication attempts found in this log file")
        st.info("💡 Make sure the file contains SSH authentication logs with failed attempts")
        return
    
    # Count IP occurrences
    ip_counter = Counter(failed_ips)
    total_attempts = len(failed_ips)
    unique_ips = len(ip_counter)
    
    # Display summary statistics
    st.success(f"✅ Analysis Complete: {total_attempts} failed attempts from {unique_ips} unique IPs")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Failed Attempts", f"{total_attempts:,}")
    with col2:
        st.metric("Unique Attacking IPs", unique_ips)
    with col3:
        most_active_ip = ip_counter.most_common(1)[0]
        st.metric("Most Active IP", most_active_ip[0], f"{most_active_ip[1]} attempts")
    
    st.markdown("---")
    
    # Get top 10 IPs for detailed analysis
    top_ips = ip_counter.most_common(10)
    
    st.subheader("🌍 Geographic Intelligence")
    st.markdown("Fetching geolocation data for top 10 attacking IPs...")
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    geo_data = []
    map_data = []
    
    for idx, (ip, count) in enumerate(top_ips):
        status_text.text(f"Analyzing {ip}... ({idx + 1}/{len(top_ips)})")
        
        geo_info = get_ip_geolocation(ip)
        
        if geo_info:
            geo_info['attempts'] = count
            geo_info['flag'] = get_country_flag_emoji(geo_info['countryCode'])
            geo_data.append(geo_info)
            
            # Add to map data if valid coordinates
            if geo_info['lat'] != 0.0 or geo_info['lon'] != 0.0:
                map_data.append({
                    'lat': geo_info['lat'],
                    'lon': geo_info['lon'],
                    'ip': ip,
                    'attempts': count
                })
        
        # Update progress
        progress_bar.progress((idx + 1) / len(top_ips))
        
        # Respect API rate limits (ip-api.com allows 45 req/min for free)
        if idx < len(top_ips) - 1:
            time.sleep(0.1)
    
    progress_bar.empty()
    status_text.empty()
    
    # Display geographic data table
    if geo_data:
        st.subheader("📊 Top Attacking IPs - Geographic Breakdown")
        
        # Create formatted DataFrame
        df = pd.DataFrame(geo_data)
        
        # Reorder and rename columns for better display
        display_df = df[[
            'flag', 'ip', 'attempts', 'country', 'city', 
            'isp', 'org', 'timezone'
        ]].copy()
        
        display_df.columns = [
            '🏳️', 'IP Address', 'Attempts', 'Country', 
            'City', 'ISP', 'Organization', 'Timezone'
        ]
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Display map
        if map_data:
            st.subheader("🗺️ Attack Origins Map")
            st.markdown("*Red markers show geographic locations of attacking IPs*")
            
            map_df = pd.DataFrame(map_data)
            st.map(map_df[['lat', 'lon']], zoom=1, use_container_width=True)
            
            # Additional insights
            st.markdown("---")
            st.subheader("📈 Attack Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Top countries
                country_counts = Counter([d['country'] for d in geo_data])
                st.markdown("**Top Countries:**")
                for country, count in country_counts.most_common(5):
                    flag = get_country_flag_emoji(
                        next(d['countryCode'] for d in geo_data if d['country'] == country)
                    )
                    st.write(f"{flag} {country}: {count} IP(s)")
            
            with col2:
                # Top ISPs
                isp_counts = Counter([d['isp'] for d in geo_data if d['isp'] != 'Unknown'])
                if isp_counts:
                    st.markdown("**Top ISPs:**")
                    for isp, count in isp_counts.most_common(5):
                        st.write(f"🏢 {isp}: {count} IP(s)")
        
        # Export option
        st.markdown("---")
        csv = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Full Report (CSV)",
            data=csv,
            file_name="ssh_forensics_report.csv",
            mime="text/csv",
        )
        
    else:
        st.error("❌ Could not retrieve geolocation data. Please check your internet connection.")
    
    # Security recommendations
    with st.expander("🛡️ Security Recommendations"):
        st.markdown("""
        ### Immediate Actions:
        - ✅ **Block attacking IPs** using fail2ban or firewall rules
        - ✅ **Disable root login** via SSH (`PermitRootLogin no`)
        - ✅ **Use SSH keys** instead of passwords
        - ✅ **Change default SSH port** (from 22 to custom port)
        - ✅ **Implement rate limiting** to prevent brute force
        - ✅ **Use allowlist** for known trusted IPs if possible
        
        ### Long-term Security:
        - 🔐 Enable **Two-Factor Authentication (2FA)** for SSH
        - 🔐 Use **fail2ban** with aggressive banning rules
        - 🔐 Implement **GeoIP blocking** for unexpected countries
        - 🔐 Monitor logs regularly with **SIEM** tools
        - 🔐 Keep systems **updated** and **patched**
        """)


