import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem

def create_manual():
    # Ensure static/docs directory exists
    docs_dir = os.path.join(os.path.dirname(__file__), 'static', 'docs')
    os.makedirs(docs_dir, exist_ok=True)
    
    pdf_path = os.path.join(docs_dir, 'ARK_Executive_Command_Manual.pdf')
    
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor='#1a1a1a'
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=10,
        textColor='#d4af37' # Gold
    )
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        spaceBefore=10,
        spaceAfter=5,
        textColor='#000000'
    )
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=10,
        leading=14
    )
    
    Story = []
    
    # Title
    Story.append(Paragraph("ARK Executive Command Center - System Manual", title_style))
    
    # 1. Executive Overview
    Story.append(Paragraph("1. Executive Overview", heading_style))
    Story.append(Paragraph("Welcome to the ARK Executive Command Center manual. This documentation is your complete guide to operating the platform from the ground up. Whether you are adding new premium assets, securing vault directories, or tracking high-profile leads, this manual will guide you step-by-step.", body_style))
    
    # 2. Dashboard
    Story.append(Paragraph("2. Dashboard & Navigation", heading_style))
    Story.append(Paragraph("The Command Center Dashboard is your central intelligence hub. Upon logging in, you are greeted with high-level analytics and critical system statuses.", body_style))
    list_items = [
        ListItem(Paragraph("<b>Lead Velocity Chart:</b> Displays the influx of new customer inquiries over the last 14 days.", body_style)),
        ListItem(Paragraph("<b>System Status Widget:</b> Indicates your connection security. The 'Sever Connection' button instantly logs you out of the platform.", body_style)),
    ]
    Story.append(ListFlowable(list_items, bulletType='bullet'))
    
    # 3. Vault Directories
    Story.append(Paragraph("3. Vault Directories (Categories)", heading_style))
    Story.append(Paragraph("Before adding any assets, you must ensure the correct categories exist. The system organizes assets into Vault Directories.", body_style))
    list_items = [
        ListItem(Paragraph("Navigate to <b>Vault Directories</b> from the sidebar.", body_style)),
        ListItem(Paragraph("<b>To Add a New Directory:</b> Enter the name (e.g., 'Armored Vehicles') and click 'Establish Directory'.", body_style)),
        ListItem(Paragraph("<b>To Edit or Delete:</b> Use the respective 'Refine' or 'Purge' buttons.", body_style)),
    ]
    Story.append(ListFlowable(list_items, bulletType='1'))
    
    # 4. The Vault
    Story.append(Paragraph("4. The Vault (Adding & Uploading Assets)", heading_style))
    Story.append(Paragraph("<b>Uploading a Single Asset:</b>", subheading_style))
    list_items = [
        ListItem(Paragraph("Navigate to <b>The Vault</b> from the sidebar.", body_style)),
        ListItem(Paragraph("Click the gold <b>'Deploy New Asset'</b> button.", body_style)),
        ListItem(Paragraph("Enter the Designation, select a Vault Directory, provide an SKU and price.", body_style)),
        ListItem(Paragraph("Upload a high-quality Media Attachment.", body_style)),
        ListItem(Paragraph("Click <b>'Secure Asset in Vault'</b>.", body_style)),
    ]
    Story.append(ListFlowable(list_items, bulletType='1'))
    
    Story.append(Paragraph("<b>Mass Deployment (Bulk Image Upload):</b>", subheading_style))
    list_items = [
        ListItem(Paragraph("From The Vault, click <b>'Mass Deployment'</b>.", body_style)),
        ListItem(Paragraph("Select a target Vault Directory.", body_style)),
        ListItem(Paragraph("Select multiple images from your computer and click 'Execute'. The system will generate temporary SKUs.", body_style)),
    ]
    Story.append(ListFlowable(list_items, bulletType='1'))
    
    # 5. Intelligence
    Story.append(Paragraph("5. Intelligence Hub (Leads)", heading_style))
    list_items = [
        ListItem(Paragraph("Navigate to <b>Intelligence</b> in the sidebar.", body_style)),
        ListItem(Paragraph("View incoming leads and inquiries.", body_style)),
        ListItem(Paragraph("Click <b>'Print Dossier'</b> to generate a formatted intelligence report.", body_style)),
    ]
    Story.append(ListFlowable(list_items, bulletType='1'))
    
    # 6. Sourcing Desk
    Story.append(Paragraph("6. Sourcing Desk (Custom Requests)", heading_style))
    list_items = [
        ListItem(Paragraph("Navigate to the <b>Sourcing Desk</b>.", body_style)),
        ListItem(Paragraph("Click on any request's Tracking Code to open the detailed view.", body_style)),
        ListItem(Paragraph("Update the status (Pending Review, In Progress, Fulfilled).", body_style)),
        ListItem(Paragraph("Add private <b>Broker Notes</b> for internal comments.", body_style)),
    ]
    Story.append(ListFlowable(list_items, bulletType='1'))
    
    # 7. Threat Console
    Story.append(Paragraph("7. Threat Console (Security)", heading_style))
    list_items = [
        ListItem(Paragraph("Review IP addresses from decoy admin logs.", body_style)),
        ListItem(Paragraph("Click the checkmark to mark a threat as 'Resolved'.", body_style)),
        ListItem(Paragraph("Click 'Purge Resolved Logs' to clean the database.", body_style)),
    ]
    Story.append(ListFlowable(list_items, bulletType='1'))
    
    doc.build(Story)
    print(f"PDF successfully created at {pdf_path}")

if __name__ == "__main__":
    create_manual()
