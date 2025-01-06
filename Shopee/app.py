from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

def calculate_pricing_shopee(sale_price, product_cost, freight_cost, discount_rate, return_insurance_rate):
    # Taxas da Shopee
    marketplace_fee = (sale_price * 0.19) + 4.00
    transaction_fee = sale_price * 0.0098
    discount = sale_price * discount_rate
    return_insurance = sale_price * return_insurance_rate

    # Preço de venda líquido (Lucro Bruto antes dos custos fixos)
    gross_profit = sale_price - (marketplace_fee + transaction_fee + discount)

    # Taxa de transporte fixa
    transport_fee = 5.76

    # Impostos sobre a nota fiscal
    tax = (sale_price + transport_fee) * 0.10

    # Lucro líquido
    net_profit = gross_profit - (product_cost + freight_cost + return_insurance + tax)

    # Margem de contribuição
    contribution_margin = net_profit / sale_price
    contribution_margin_percentage = contribution_margin * 100

    # ROI
    roi = net_profit / product_cost

    # Preço sugerido para 15% de margem de contribuição
    desired_margin = 0.15
    total_cost = product_cost + freight_cost + return_insurance + tax
    suggested_sale_price = total_cost / (1 - desired_margin - (0.19 + 0.0098))

    return {
        "sale_price": sale_price,
        "suggested_sale_price": suggested_sale_price,
        "marketplace_fee": marketplace_fee,
        "transaction_fee": transaction_fee,
        "transport_fee": transport_fee,
        "return_insurance": return_insurance,
        "tax": tax,
        "discount": discount,
        "gross_profit": gross_profit,
        "net_profit": net_profit,
        "contribution_margin_percentage": contribution_margin_percentage,
        "roi": roi
    }

@app.route('/', methods=['GET'])
def index():
    return render_template('form.html')

@app.route('/', methods=['POST'])
def calculate():
    sale_price = float(request.form['sale_price'])
    product_cost = float(request.form['product_cost'])
    freight_cost = float(request.form['freight_cost'])
    discount_rate = float(request.form.get('discount_rate', 0)) / 100
    return_insurance_rate = float(request.form.get('return_insurance_rate', 0)) / 100

    results = calculate_pricing_shopee(sale_price, product_cost, freight_cost, discount_rate, return_insurance_rate)

    highlight_color = "blue" if results['net_profit'] > 0 else "red"

    fig, ax = plt.subplots()
    categories = ['Tarifa Shopee', 'Frete', 'Impostos', 'Desconto', 'Seguro', 'Lucro Líquido']
    values = [
        results['marketplace_fee'],
        results['transport_fee'],
        results['tax'],
        results['discount'],
        results['return_insurance'],
        results['net_profit']
    ]
    bars = ax.bar(categories, values, color=["gray", "gray", "gray", "gray", "gray", highlight_color])
    ax.set_title('Distribuição de Custos (Shopee)')
    ax.set_ylabel('Valor (R$)')

    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, yval + 0.1, round(yval, 2), ha='center')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    graph_url = base64.b64encode(buf.getvalue()).decode('utf8')
    buf.close()

    return render_template('results.html',
                           results=results,
                           graph_url=graph_url,
                           highlight_color=highlight_color)

if __name__ == '__main__':
    app.run(debug=True)
