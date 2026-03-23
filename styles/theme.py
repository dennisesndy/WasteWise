"""
CSS styling for the application.
"""

def get_custom_css():
    return """
    <style>
        @import url('[fonts.googleapis.com](https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;600;700&family=DM+Serif+Display:ital@0;1&display=swap)');

        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
            background-color: #f7faf8;
        }

        /* Hero Header */
        .main-header {
            background: linear-gradient(135deg, #0d2b1d 0%, #163d2b 45%, #1e5438 100%);
            padding: 1.8rem 2rem;
            border-radius: 16px;
            margin-bottom: 1.5rem;
            color: white;
            position: relative;
            overflow: hidden;
        }
        .main-header::before {
            content: '';
            position: absolute;
            inset: 0;
            background: radial-gradient(ellipse at 80% 50%, rgba(82,183,136,0.18) 0%, transparent 65%);
            pointer-events: none;
        }
        .main-header h1 {
            font-family: 'DM Serif Display', serif;
            font-size: 2.2rem;
            font-weight: 400;
            margin: 0;
        }
        .main-header p {
            font-size: 0.95rem;
            opacity: 0.8;
            margin: 0.3rem 0 0;
        }

        /* Section Title */
        .section-title {
            font-family: 'DM Serif Display', serif;
            font-size: 1.15rem;
            color: #163d2b;
            border-left: 3px solid #52b788;
            padding-left: 0.7rem;
            margin: 1.4rem 0 0.8rem;
        }

        /* Metric Cards */
        .metric-card {
            background: white;
            border-radius: 12px;
            padding: 1rem 1.2rem;
            border-top: 3px solid #52b788;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            margin-bottom: 0.4rem;
        }
        .metric-card.danger { border-top-color: #e63946; }
        .metric-card.warning { border-top-color: #f4a261; }
        .metric-card.safe { border-top-color: #52b788; }
        .metric-card.arima { border-top-color: #457b9d; }
        .metric-card.cluster { border-top-color: #8b5cf6; }

        .metric-card .label {
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #6b7280;
            font-weight: 600;
        }
        .metric-card .value {
            font-family: 'DM Serif Display', serif;
            font-size: 1.8rem;
            color: #111827;
            margin-top: 0.1rem;
        }
        .metric-card .sub {
            font-size: 0.75rem;
            color: #9ca3af;
        }

        /* Insight Boxes */
        .insight-box {
            background: #f0fdf4;
            border: 1px solid #86efac;
            border-radius: 8px;
            padding: 0.8rem 1rem;
            font-size: 0.85rem;
            color: #166534;
            margin: 0.4rem 0;
        }
        .insight-box.warn { background: #fff7ed; border-color: #fdba74; color: #9a3412; }
        .insight-box.info { background: #eff6ff; border-color: #93c5fd; color: #1e40af; }
        .insight-box.cluster { background: #f5f3ff; border-color: #c4b5fd; color: #5b21b6; }

        /* Product Badge */
        .product-badge {
            display: inline-block;
            background: #d1fae5;
            color: #065f46;
            font-size: 0.9rem;
            font-weight: 700;
            padding: 0.3rem 1rem;
            border-radius: 50px;
            border: 1.5px solid #6ee7b7;
            margin-bottom: 0.8rem;
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #f3f4f6;
            border-radius: 8px;
            padding: 8px 16px;
        }

        /* Sidebar */
        .stSidebar { background-color: #f3f6f4 !important; }
    </style>
    """
