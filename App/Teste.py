import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def numero(valor):
    if pd.isna(valor):
        return np.nan

    if isinstance(valor, (int, float, np.integer, np.floating)):
        return float(valor)

    texto = str(valor).strip()
    texto = texto.replace("mm", "")
    texto = texto.replace("m", "")
    texto = texto.replace(",", ".")

    try:
        return float(texto)
    except:
        return np.nan

def ler_excel(arquivo):
    excel = pd.ExcelFile(arquivo)

    if "Tabela_Cotas" in excel.sheet_names:
        tabela = pd.read_excel(
            arquivo,
            sheet_name="Tabela_Cotas",
            header=None
        )

        dados = interpretar_tabela_cotas(tabela)

        if dados is not None and len(dados) > 0:
            return dados

    for aba in excel.sheet_names:
        tabela = pd.read_excel(
            arquivo,
            sheet_name=aba,
            header=None
        )

        dados = interpretar_tabela_cotas(tabela)

        if dados is not None and len(dados) > 0:
            return dados

    raise ValueError(
        "Não foi possível identificar a tabela de cotas.\n\n"
        "O formato esperado é:\n"
        "WL | Z | ST 00 | ST 01 | ST 02...\n"
        "   | X | valor | valor | valor...\n"
        "100|100| cota  | cota  | cota...\n"
        "200|200| cota  | cota  | cota..."
    )


def interpretar_tabela_cotas(tabela):

    if tabela.empty:
        return None

    estacoes = []
    colunas = []

    for c in range(2, tabela.shape[1]):

        valor = tabela.iloc[0, c]

        try:
            valor = float(valor)
        except:
            continue

        if np.isfinite(valor):

            estacoes.append(
                int(round(valor))
            )

            colunas.append(c)

    if len(estacoes) < 2:
        return None

    x_values = []

    for c in colunas:

        x = pd.to_numeric(
            tabela.iloc[1, c],
            errors="coerce"
        )

        if pd.isna(x):
            return None

        x_values.append(
            float(x)
        )

    dados = []

    for r in range(2, tabela.shape[0]):

        wl = pd.to_numeric(
            tabela.iloc[r, 0],
            errors="coerce"
        )

        z = pd.to_numeric(
            tabela.iloc[r, 1],
            errors="coerce"
        )

        if pd.isna(wl):
            continue

        if pd.isna(z):
            z = wl

        for i, c in enumerate(colunas):

            y = pd.to_numeric(
                tabela.iloc[r, c],
                errors="coerce"
            )

            if pd.isna(y):
                continue

            dados.append({
                "ST": estacoes[i],
                "X": x_values[i],
                "WL": float(wl),
                "Z": float(z),
                "Y": float(y)
            })

    if len(dados) == 0:
        return None

    resultado = pd.DataFrame(dados)

    resultado = resultado.drop_duplicates(
        subset=["ST", "WL"]
    )

    resultado = resultado.sort_values(
        ["ST", "WL"]
    )

    return resultado.reset_index(drop=True)
def interpretar_tabela(tabela):
    linhas = tabela.shape[0]
    colunas = tabela.shape[1]

    blocos = []

    for r in range(linhas - 1):

        valores = []

        for c in range(colunas):
            valores.append(numero(tabela.iloc[r, c]))

        indices = []

        for c, valor in enumerate(valores):
            if not np.isnan(valor):
                if abs(valor - round(valor)) < 1e-8:
                    inteiro = int(round(valor))
                    if inteiro >= 0:
                        indices.append((c, inteiro))

        sequencias = []

        for inicio in range(len(indices)):
            sequencia = [indices[inicio]]

            esperado = indices[inicio][1] + 1

            for j in range(inicio + 1, len(indices)):
                pos, valor = indices[j]

                if valor == esperado:
                    sequencia.append((pos, valor))
                    esperado += 1
                else:
                    break

            if len(sequencia) >= 3:
                sequencias.append(sequencia)

        for sequencia in sequencias:

            colunas_estacoes = [x[0] for x in sequencia]
            numeros_estacoes = [x[1] for x in sequencia]

            linha_x = r + 1

            x_values = []

            for c in colunas_estacoes:
                x_values.append(
                    numero(tabela.iloc[linha_x, c])
                )

            quantidade_x = sum(
                not np.isnan(x) for x in x_values
            )

            if quantidade_x < 3:
                continue

            for rr in range(linha_x + 1, linhas):

                primeira = numero(
                    tabela.iloc[rr, 0]
                )

                segunda = numero(
                    tabela.iloc[rr, 1]
                )

                if np.isnan(primeira) or np.isnan(segunda):
                    continue

                if primeira < 0 or primeira > 100:
                    continue

                if abs(primeira - round(primeira)) > 1e-8:
                    continue

                wl = int(round(primeira))
                z = segunda

                pontos = []

                for i, c in enumerate(colunas_estacoes):

                    y = numero(
                        tabela.iloc[rr, c]
                    )

                    x = x_values[i]

                    if not np.isnan(x) and not np.isnan(y):

                        pontos.append({
                            "ST": numeros_estacoes[i],
                            "X": x,
                            "WL": wl,
                            "Z": z,
                            "Y": y
                        })

                if len(pontos) >= 2:
                    blocos.extend(pontos)

    if not blocos:
        return None

    dados = pd.DataFrame(blocos)

    dados = dados.drop_duplicates(
        subset=["ST", "WL"]
    )

    dados = dados.sort_values(
        ["ST", "WL"]
    )

    return dados.reset_index(drop=True)


def interpolar_curva(x, y, quantidade=200):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    mascara = (
        np.isfinite(x)
        &
        np.isfinite(y)
    )

    x = x[mascara]
    y = y[mascara]

    if len(x) < 2:
        return None, None

    ordem = np.argsort(x)

    x = x[ordem]
    y = y[ordem]

    x_unico, indices = np.unique(
        x,
        return_index=True
    )

    y_unico = y[indices]

    if len(x_unico) < 2:
        return None, None

    xx = np.linspace(
        x_unico.min(),
        x_unico.max(),
        quantidade
    )

    try:
        from scipy.interpolate import PchipInterpolator

        interpolador = PchipInterpolator(
            x_unico,
            y_unico
        )

        yy = interpolador(xx)

    except:
        yy = np.interp(
            xx,
            x_unico,
            y_unico
        )

    return xx, yy


def plano_balizas(dados, salvar=None):
    fig, ax = plt.subplots(
        figsize=(10, 8)
    )

    estacoes = sorted(
        dados["ST"].unique()
    )

    for st in estacoes:

        secao = dados[
            dados["ST"] == st
        ].sort_values("Z")

        if len(secao) < 2:
            continue

        y = secao["Y"].values
        z = secao["Z"].values

        xx, yy = interpolar_curva(
            y,
            z
        )

        if xx is None:
            continue

        ax.plot(
            xx,
            yy,
            linewidth=1.5
        )

        ax.plot(
            -xx,
            yy,
            linewidth=1.0
        )

        ax.text(
            xx.max(),
            yy.max(),
            f"ST {int(st):02d}",
            fontsize=8
        )

    ax.axvline(
        0,
        linewidth=0.8
    )

    ax.set_title(
        "PLANO DE LINHAS DE BALIZAS",
        fontsize=15,
        fontweight="bold"
    )

    ax.set_xlabel(
        "Meia-boca Y [mm]"
    )

    ax.set_ylabel(
        "Altura Z [mm]"
    )

    ax.grid(
        True,
        alpha=0.3
    )

    ax.set_aspect(
        "equal",
        adjustable="box"
    )

    fig.tight_layout()

    if salvar:
        fig.savefig(
            salvar,
            dpi=300,
            bbox_inches="tight"
        )

    return fig


def plano_linhas_dagua(dados, salvar=None):
    fig, ax = plt.subplots(
        figsize=(13, 7)
    )

    wls = sorted(
        dados["WL"].unique()
    )

    estacoes = sorted(
        dados["ST"].unique()
    )

    for wl in wls:

        secao = dados[
            dados["WL"] == wl
        ].sort_values("X")

        if len(secao) < 2:
            continue

        x = secao["X"].values
        y = secao["Y"].values

        xx, yy = interpolar_curva(
            x,
            y
        )

        if xx is None:
            continue

        ax.plot(
            xx,
            yy,
            linewidth=1.5
        )

        ax.plot(
            xx,
            -yy,
            linewidth=1.0
        )

        ax.text(
            xx[-1],
            yy[-1],
            f"WL {int(wl):02d}",
            fontsize=8
        )

    for st in estacoes:

        secao = dados[
            dados["ST"] == st
        ]

        if len(secao) < 2:
            continue

        x = secao["X"].iloc[0]

        ax.axvline(
            x,
            linewidth=0.35,
            alpha=0.5
        )

        ax.text(
            x,
            0,
            f"ST {int(st):02d}",
            rotation=90,
            fontsize=7,
            verticalalignment="bottom"
        )

    ax.axhline(
        0,
        linewidth=0.8
    )

    ax.set_title(
        "PLANO DE LINHAS D'ÁGUA",
        fontsize=15,
        fontweight="bold"
    )

    ax.set_xlabel(
        "Comprimento / posição longitudinal X [mm]"
    )

    ax.set_ylabel(
        "Meia-boca Y [mm]"
    )

    ax.grid(
        True,
        alpha=0.3
    )

    ax.set_aspect(
        "equal",
        adjustable="box"
    )

    fig.tight_layout()

    if salvar:
        fig.savefig(
            salvar,
            dpi=300,
            bbox_inches="tight"
        )

    return fig


def plano_linhas_alto(dados, salvar=None):
    fig, ax = plt.subplots(
        figsize=(13, 7)
    )

    valores_y = dados["Y"].values

    valores_y = valores_y[
        np.isfinite(valores_y)
    ]

    if len(valores_y) == 0:
        raise ValueError(
            "Não existem valores de meia-boca."
        )

    y_max = np.max(
        np.abs(valores_y)
    )

    quantidade = 8

    niveis = np.linspace(
        0,
        y_max,
        quantidade + 2
    )[1:-1]

    estacoes = sorted(
        dados["ST"].unique()
    )

    for y0 in niveis:

        pontos_x = []
        pontos_z = []

        for st in estacoes:

            secao = dados[
                dados["ST"] == st
            ].copy()

            secao = secao.sort_values(
                "Y"
            )

            y = secao["Y"].values
            z = secao["Z"].values

            mascara = (
                np.isfinite(y)
                &
                np.isfinite(z)
            )

            y = y[mascara]
            z = z[mascara]

            if len(y) < 2:
                continue

            ordem = np.argsort(y)

            y = y[ordem]
            z = z[ordem]

            y_unico, indices = np.unique(
                y,
                return_index=True
            )

            z_unico = z[indices]

            if (
                y0 >= y_unico.min()
                and
                y0 <= y_unico.max()
            ):

                z0 = np.interp(
                    y0,
                    y_unico,
                    z_unico
                )

                pontos_x.append(
                    secao["X"].iloc[0]
                )

                pontos_z.append(
                    z0
                )

        if len(pontos_x) >= 2:

            xx, zz = interpolar_curva(
                pontos_x,
                pontos_z
            )

            if xx is not None:

                ax.plot(
                    xx,
                    zz,
                    linewidth=1.5
                )

                ax.text(
                    xx[-1],
                    zz[-1],
                    f"LB {y0:.0f}",
                    fontsize=8
                )

    for st in estacoes:

        secao = dados[
            dados["ST"] == st
        ]

        if len(secao) < 2:
            continue

        x = secao["X"].iloc[0]

        ax.axvline(
            x,
            linewidth=0.35,
            alpha=0.5
        )

        ax.text(
            x,
            0,
            f"ST {int(st):02d}",
            rotation=90,
            fontsize=7,
            verticalalignment="bottom"
        )

    ax.axhline(
        0,
        linewidth=0.8
    )

    ax.set_title(
        "PLANO DE LINHAS DO ALTO",
        fontsize=15,
        fontweight="bold"
    )

    ax.set_xlabel(
        "Comprimento / posição longitudinal X [mm]"
    )

    ax.set_ylabel(
        "Altura Z [mm]"
    )

    ax.grid(
        True,
        alpha=0.3
    )

    fig.tight_layout()

    if salvar:
        fig.savefig(
            salvar,
            dpi=300,
            bbox_inches="tight"
        )

    return fig


def gerar_plano_completo(dados, pasta):
    pasta = Path(pasta)

    pasta.mkdir(
        parents=True,
        exist_ok=True
    )

    arquivo_balizas = (
        pasta /
        "01_PLANO_DE_BALIZAS.png"
    )

    arquivo_agua = (
        pasta /
        "02_PLANO_DE_LINHAS_DAGUA.png"
    )

    arquivo_alto = (
        pasta /
        "03_PLANO_DE_LINHAS_DO_ALTO.png"
    )

    fig1 = plano_balizas(
        dados,
        arquivo_balizas
    )

    plt.close(fig1)

    fig2 = plano_linhas_dagua(
        dados,
        arquivo_agua
    )

    plt.close(fig2)

    fig3 = plano_linhas_alto(
        dados,
        arquivo_alto
    )

    plt.close(fig3)


class Aplicacao:

    def __init__(self, janela):

        self.janela = janela

        self.janela.title(
            "Gerador de Plano de Linhas - Arquitetura Naval"
        )

        self.janela.geometry(
            "850x600"
        )

        self.dados = None
        self.arquivo = None

        frame = ttk.Frame(
            janela,
            padding=25
        )

        frame.pack(
            fill="both",
            expand=True
        )

        titulo = ttk.Label(
            frame,
            text="GERADOR DE PLANO DE LINHAS",
            font=(
                "Arial",
                20,
                "bold"
            )
        )

        titulo.pack(
            pady=(0, 10)
        )

        subtitulo = ttk.Label(
            frame,
            text=(
                "Balizas  |  Linhas d'Água  |  Linhas do Alto"
            ),
            font=(
                "Arial",
                11
            )
        )

        subtitulo.pack(
            pady=(0, 25)
        )

        arquivo_frame = ttk.LabelFrame(
            frame,
            text="Planilha de cotas",
            padding=15
        )

        arquivo_frame.pack(
            fill="x",
            pady=10
        )

        self.nome_arquivo = ttk.Label(
            arquivo_frame,
            text="Nenhuma planilha selecionada."
        )

        self.nome_arquivo.pack(
            side="left",
            fill="x",
            expand=True
        )

        botao_abrir = ttk.Button(
            arquivo_frame,
            text="SELECIONAR EXCEL",
            command=self.abrir
        )

        botao_abrir.pack(
            side="right"
        )

        info = ttk.LabelFrame(
            frame,
            text="Dados identificados",
            padding=15
        )

        info.pack(
            fill="x",
            pady=15
        )

        self.label_estacoes = ttk.Label(
            info,
            text="Estações: -"
        )

        self.label_estacoes.grid(
            row=0,
            column=0,
            padx=15,
            pady=5,
            sticky="w"
        )

        self.label_wl = ttk.Label(
            info,
            text="Linhas d'água: -"
        )

        self.label_wl.grid(
            row=0,
            column=1,
            padx=15,
            pady=5,
            sticky="w"
        )

        self.label_pontos = ttk.Label(
            info,
            text="Pontos: -"
        )

        self.label_pontos.grid(
            row=1,
            column=0,
            padx=15,
            pady=5,
            sticky="w"
        )

        self.label_comprimento = ttk.Label(
            info,
            text="Comprimento: -"
        )

        self.label_comprimento.grid(
            row=1,
            column=1,
            padx=15,
            pady=5,
            sticky="w"
        )

        botoes = ttk.LabelFrame(
            frame,
            text="Visualização",
            padding=15
        )

        botoes.pack(
            fill="x",
            pady=10
        )

        ttk.Button(
            botoes,
            text="PLANO DE BALIZAS",
            command=self.mostrar_balizas
        ).pack(
            side="left",
            padx=5,
            expand=True,
            fill="x"
        )

        ttk.Button(
            botoes,
            text="LINHAS D'ÁGUA",
            command=self.mostrar_agua
        ).pack(
            side="left",
            padx=5,
            expand=True,
            fill="x"
        )

        ttk.Button(
            botoes,
            text="LINHAS DO ALTO",
            command=self.mostrar_alto
        ).pack(
            side="left",
            padx=5,
            expand=True,
            fill="x"
        )

        botao_gerar = ttk.Button(
            frame,
            text="GERAR PLANO COMPLETO E SALVAR",
            command=self.gerar
        )

        botao_gerar.pack(
            pady=25,
            ipadx=30,
            ipady=12
        )

        self.status = ttk.Label(
            frame,
            text="Selecione a planilha de cotas."
        )

        self.status.pack(
            pady=10
        )

    def abrir(self):

        arquivo = filedialog.askopenfilename(
            title="Selecione a tabela de cotas",
            filetypes=[
                (
                    "Excel",
                    "*.xlsx *.xls"
                ),
                (
                    "Todos os arquivos",
                    "*.*"
                )
            ]
        )

        if not arquivo:
            return

        try:

            dados = ler_excel(
                arquivo
            )

            self.dados = dados
            self.arquivo = arquivo

            estacoes = sorted(
                dados["ST"].unique()
            )

            wls = sorted(
                dados["WL"].unique()
            )

            comprimento = (
                dados["X"].min(),
                dados["X"].max()
            )

            self.nome_arquivo.config(
                text=Path(
                    arquivo
                ).name
            )

            self.label_estacoes.config(
                text=(
                    f"Estações: {len(estacoes)} "
                    f"(ST {int(min(estacoes)):02d} "
                    f"até ST {int(max(estacoes)):02d})"
                )
            )

            self.label_wl.config(
                text=(
                    f"Linhas d'água: {len(wls)}"
                )
            )

            self.label_pontos.config(
                text=(
                    f"Pontos: {len(dados)}"
                )
            )

            self.label_comprimento.config(
                text=(
                    f"Comprimento: "
                    f"{comprimento[1] - comprimento[0]:.2f} mm"
                )
            )

            self.status.config(
                text="Planilha carregada com sucesso."
            )

        except Exception as erro:

            self.dados = None

            messagebox.showerror(
                "Erro ao ler planilha",
                str(erro)
            )

    def verificar(self):

        if self.dados is None:

            messagebox.showwarning(
                "Atenção",
                "Primeiro selecione uma planilha."
            )

            return False

        return True

    def mostrar_balizas(self):

        if not self.verificar():
            return

        plano_balizas(
            self.dados
        )

        plt.show()

    def mostrar_agua(self):

        if not self.verificar():
            return

        plano_linhas_dagua(
            self.dados
        )

        plt.show()

    def mostrar_alto(self):

        if not self.verificar():
            return

        plano_linhas_alto(
            self.dados
        )

        plt.show()

    def gerar(self):

        if not self.verificar():
            return

        pasta = filedialog.askdirectory(
            title="Escolha a pasta para salvar o plano"
        )

        if not pasta:
            return

        try:

            gerar_plano_completo(
                self.dados,
                pasta
            )

            fig1 = plano_balizas(
                self.dados
            )

            plt.show(
                block=False
            )

            fig2 = plano_linhas_dagua(
                self.dados
            )

            plt.show(
                block=False
            )

            fig3 = plano_linhas_alto(
                self.dados
            )

            plt.show()

            messagebox.showinfo(
                "Concluído",
                (
                    "Plano de linhas gerado com sucesso!\n\n"
                    f"Arquivos salvos em:\n{pasta}\n\n"
                    "Foram gerados:\n"
                    "01_PLANO_DE_BALIZAS.png\n"
                    "02_PLANO_DE_LINHAS_DAGUA.png\n"
                    "03_PLANO_DE_LINHAS_DO_ALTO.png"
                )
            )

        except Exception as erro:

            messagebox.showerror(
                "Erro na geração",
                str(erro)
            )


if __name__ == "__main__":

    janela = tk.Tk()

    aplicativo = Aplicacao(
        janela
    )

    janela.mainloop()