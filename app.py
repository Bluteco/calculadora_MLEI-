# Importando as bibliotecas necessárias
from flask import Flask, render_template, request
from flask_cors import CORS  # Adicionando suporte a CORS
import matplotlib
import matplotlib.pyplot as plt
import io
import base64

# Configurando o backend do Matplotlib para evitar problemas de interface gráfica
matplotlib.use('Agg')

# Criando a aplicação Flask
app = Flask(__name__)

# Função para calcular a precificação no Mercado Livre
def calculate_pricing_mercado_livre(sale_price, product_cost, freight_cost, category_rate, return_insurance_rate):
    marketplace_fee = sale_price * category_rate
    freight_median_below_79 = 19.90
    fixed_fee = 6.75 if sale_price < 79 else 0.00

    if sale_price < 79:
        tax = (sale_price + freight_median_below_79) * 0.10
        freight_used = 0.00
        gross_profit_initial = sale_price - marketplace_fee - fixed_fee
    else:
        tax = (sale_price + freight_cost) * 0.10
        freight_used = freight_cost
        gross_profit_initial = sale_price - marketplace_fee - freight_cost

    return_insurance = sale_price * return_insurance_rate
    net_profit = gross_profit_initial - (product_cost + tax + return_insurance)

    contribution_margin = net_profit / sale_price
    contribution_margin_percentage = contribution_margin * 100
    roi = net_profit / product_cost

    return {
        "marketplace_fee": marketplace_fee,
        "freight_used": freight_used,
        "fixed_fee": fixed_fee,
        "gross_profit_initial": gross_profit_initial,
        "tax": tax,
        "return_insurance": return_insurance,
        "net_profit": net_profit,
        "contribution_margin_percentage": contribution_margin_percentage,
        "roi": roi
    }

# Rota principal do Flask para exibir o formulário e os resultados
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Obtendo os dados do formulário
        sale_price = float(request.form['sale_price'])
        product_cost = float(request.form['product_cost'])
        freight_cost = float(request.form['freight_cost'])
        category_rate = float(request.form['category_rate']) / 100
        return_insurance_rate = float(request.form['return_insurance_rate']) / 100

        # Realizando os cálculos
        results = calculate_pricing_mercado_livre(sale_price, product_cost, freight_cost, category_rate, return_insurance_rate)

        # Determinando a cor do destaque (lucro ou prejuízo)
        highlight_color = "blue" if results['net_profit'] > 0 else "red"

        # Gerando o gráfico para visualização
        fig, ax = plt.subplots()
        categories = ['Tarifa', 'Frete', 'Lucro Bruto', 'Impostos', 'Seguro', 'Lucro Líquido']
        values = [
            results['marketplace_fee'],
            results['freight_used'],
            results['gross_profit_initial'],
            results['tax'],
            results['return_insurance'],
            results['net_profit']
        ]
        bars = ax.bar(categories, values, color=["gray", "gray", "blue", "gray", "gray", highlight_color])
        ax.set_title('Distribuição de Custos (Mercado Livre)')
        ax.set_ylabel('Valor (R$)')

        # Adicionando os valores no topo das barras
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + 0.1, round(yval, 2), ha='center')

        # Salvando o gráfico em um buffer para exibição
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)  # Fechando o gráfico para evitar conflitos
        buf.seek(0)
        graph_url = base64.b64encode(buf.getvalue()).decode('utf8')
        buf.close()

        return render_template('results.html',
                               results=results,
                               graph_url=graph_url,
                               highlight_color=highlight_color,
                               sale_price=sale_price)

    return render_template('form.html')

# Executando o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
