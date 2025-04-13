import gradio as gr
import PyPDF2
import google.generativeai as genai
import re

GEMINI_API_KEY = "GOOGLE_API_KEY"  # Replace with your actual key
genai.configure(api_key=GEMINI_API_KEY)

def extract_text_from_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text.strip()
    except:
        return ""

def extract_section(full_text, label):
    pattern = rf"\*\*\- {re.escape(label)}:\*\*\s*(.*?)(?=\n\*\*|\Z)"
    match = re.search(pattern, full_text, re.DOTALL)
    return match.group(1).strip() if match else "❓ Not found"

def analyze_financial_data(file):
    text = extract_text_from_pdf(file)

    if not text:
        return (
            "⚠️ Failed to extract text from the PDF. Ensure it’s not scanned.",
            "", "", "", "", "", ""
        )

    prompt = f"""
    Analyze the following Paytm transaction history and generate financial insights in the following structure:
    **Financial Insights**
    **- Monthly Income & Expenses:** [data]
    **- Unnecessary Expense Categories:** [data]
    **- Estimated Savings %:** [data]
    **- Spending Trends:** [data]
    **- Category-wise Expense Breakdown (Partial):** [data]
    **- Cost Control Suggestions:** [data]
    Transaction History:
    {text}
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        full_text = response.text.strip()

        return (
            "✅ Analysis Complete",
            extract_section(full_text, "Monthly Income & Expenses"),
            extract_section(full_text, "Unnecessary Expense Categories"),
            extract_section(full_text, "Estimated Savings %"),
            extract_section(full_text, "Spending Trends"),
            extract_section(full_text, "Category-wise Expense Breakdown (Partial)"),
            extract_section(full_text, "Cost Control Suggestions"),
        )

    except Exception as e:
        return (f"❌ Gemini Error: {e}", "", "", "", "", "", "")

gr.Interface(
    fn=analyze_financial_data,
    inputs=gr.File(label="📂 Upload Paytm PDF", file_types=[".pdf"]),
    outputs=[
        gr.Textbox(label="✅ Status", lines=2, interactive=False),
        gr.Textbox(label="💵 Monthly Income & Expenses", lines=8, interactive=False),
        gr.Textbox(label="🛒 Unnecessary Expense Categories", lines=8, interactive=False),
        gr.Textbox(label="💰 Estimated Savings %", lines=4, interactive=False),
        gr.Textbox(label="📈 Spending Trends", lines=8, interactive=False),
        gr.Textbox(label="📊 Category-wise Breakdown", lines=10, interactive=False),
        gr.Textbox(label="🧠 Cost Control Suggestions", lines=8, interactive=False),
    ],
    title="💰 AI-Powered Personal Finance Assistant",
    description="Upload your Paytm transaction PDF (text-based) and get structured financial insights using Gemini AI.",
).launch()
