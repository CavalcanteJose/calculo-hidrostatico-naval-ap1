# -*- coding: utf-8 -*-
# Circuitos Elétricos II — Resolução da Lista Teórica T1: Senóides
# Discente: Luiz Eduardo da Silva de Oliveira
# Matrícula: 2215180015

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Customização da apresentação visual dos gráficos
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams.update({
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 10,
    'figure.titlesize': 13
})


# Q1: Implementação orientada a dicionários e formatação com unidades de engenharia
dados_q1 = {
    'a': ('200 Hz', 200.0),
    'b': ('40 MHz', 40.0e6),
    'c': ('20 kHz', 20.0e3),
    'd': ('1 Hz', 1.0)
}

def formatar_tempo(t_seg):
    if t_seg >= 1:
        return f"{t_seg:.4f} s"
    elif t_seg >= 1e-3:
        return f"{t_seg*1e3:.4f} ms"
    elif t_seg >= 1e-6:
        return f"{t_seg*1e6:.4f} us"
    else:
        return f"{t_seg*1e9:.4f} ns"

print("--- Resolução da Questão 1 ---")
for chave, (rotulo, freq) in dados_q1.items():
    periodo = 1.0 / freq
    print(f"[{chave}] f = {rotulo:<10} -> T = {formatar_tempo(periodo)} ({periodo:.2e} s)")


# Q2: Determinação temporal e visualização de 5 ciclos
frequencia_q2 = 1000.0  # Hz
N_ciclos = 5
T_unitario = 1.0 / frequencia_q2
delta_t_total = N_ciclos * T_unitario

print(f"Questão 2 -> Tempo decorrido para 5 ciclos: {delta_t_total:.4f} s ({delta_t_total*1000:.1f} ms)")

t_sim = np.linspace(0, delta_t_total, 1200)
sinal_q2 = np.sin(2 * np.pi * frequencia_q2 * t_sim)

fig, ax = plt.subplots(figsize=(9, 3.8))
ax.plot(t_sim * 1e3, sinal_q2, color='#1f77b4', lw=1.8, label=r'$s(t) = \sin(2000\pi t)$')
for k in range(1, N_ciclos + 1):
    ax.axvline(k * T_unitario * 1e3, color='crimson', linestyle=':', alpha=0.7)
    ax.text(k * T_unitario * 1e3 - 0.7, 0.5, f'Ciclo {k}', color='crimson', fontsize=8)

ax.set_title('Questão 2 — Simulação Temporal: 5 Ciclos Completos de 1 kHz')
ax.set_xlabel('Tempo t (ms)')
ax.set_ylabel('Amplitude Normalizada')
ax.legend(loc='upper right')
plt.tight_layout()
plt.show()


# Q3: Pulsação angular omega
dados_q3 = {
    'a': ('1.8 s', 1.8),
    'b': ('0.3 ms', 0.3e-3),
    'c': ('8 us', 8.0e-6),
    'd': ('4x10^-6 s', 4.0e-6)
}

print("--- Resolução da Questão 3 ---")
for item, (str_T, T_val) in dados_q3.items():
    omega = 2 * np.pi / T_val
    print(f"Item ({item}) T = {str_T:<12} -> omega = {omega:>14.4f} rad/s (ou {omega/np.pi:.2f}*pi rad/s)")


# Q4: Extração analítica de Amplitude e Frequência Fundamental
sinais_q4 = [
    ('a', '20 sen(377t)', 20.0, 377.0),
    ('b', '12 sen(2*pi*120t)', 12.0, 2*np.pi*120.0),
    ('c', '10^6 sen(10000t)', 1.0e6, 10000.0),
    ('d', '-8 sen(10058t)', 8.0, 10058.0)
]

print("--- Resolução da Questão 4 ---")
for k, expr, amp, w_rad in sinais_q4:
    freq_hz = w_rad / (2 * np.pi)
    print(f"[{k}] {expr:<22} -> Amplitude = {amp:,.1f} | Frequência = {freq_hz:,.2f} Hz")


# Q5: Período e frequência com plotagem de 2 ciclos
omega_q5 = 400.0
f_q5 = omega_q5 / (2 * np.pi)
T_q5 = 1.0 / f_q5

print("--- Resolução da Questão 5 ---")
print(f"Frequência cíclica (f): {f_q5:.4f} Hz")
print(f"Período fundamental (T): {T_q5*1000:.4f} ms ({T_q5:.6f} s)")

t_eixo = np.linspace(0, 2 * T_q5, 1000)
i_sinal = 5.0 * np.cos(omega_q5 * t_eixo - np.radians(120))

fig, ax = plt.subplots(figsize=(9, 3.8))
ax.plot(t_eixo * 1000, i_sinal, color='forestgreen', lw=2, label=r'$i(t) = 5\cos(400t - 120^\circ)\ \mathrm{A}$')
ax.axhline(0, color='black', lw=0.6, ls='--')
ax.set_title('Questão 5 — Resposta Temporal de i(t) em 2 Ciclos')
ax.set_xlabel('Tempo (ms)')
ax.set_ylabel('Corrente (A)')
ax.legend(loc='upper right')
plt.tight_layout()
plt.show()


# Q6: Resolução algébrica e pontos críticos no gráfico
w6 = 800.0
Im6 = 125.0
phi_deg = 36.87
phi_rad = np.radians(phi_deg)

f6 = w6 / (2 * np.pi)
T6_ms = (1.0 / f6) * 1000
i0 = Im6 * np.cos(phi_rad)
t_raiz_ms = ((np.pi/2 - phi_rad) / w6) * 1000
t_crit_ms = ((np.pi - phi_rad) / w6) * 1000

print("--- Resolução da Questão 6 ---")
print(f"(a) f = {f6:.3f} Hz")
print(f"(b) T = {T6_ms:.3f} ms")
print(f"(c) Im = {Im6:.1f} mA")
print(f"(d) i(0) = {i0:.2f} mA")
print(f"(e) phi = {phi_deg:.2f} graus ({phi_rad:.4f} rad)")
print(f"(f) Menor t > 0 onde i(t)=0: t = {t_raiz_ms:.4f} ms")
print(f"(g) Menor t > 0 onde di/dt=0: t = {t_crit_ms:.4f} ms")

t_plot = np.linspace(0, T6_ms, 1000)
i_plot = Im6 * np.cos(w6 * (t_plot/1000) + phi_rad)

fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(t_plot, i_plot, color='#34495e', lw=2, label=r'$i(t) = 125\cos(800t + 36.87^\circ)\ \mathrm{mA}$')
ax.plot(0, i0, 'o', color='purple', label=f'i(0) = {i0:.1f} mA')
ax.plot(t_raiz_ms, 0, 's', color='crimson', label=f'Raiz: t = {t_raiz_ms:.3f} ms')
ax.plot(t_crit_ms, -Im6, '^', color='teal', label=f'Minimo: t = {t_crit_ms:.3f} ms')
ax.axhline(0, color='gray', lw=0.8, ls=':')
ax.set_title('Questão 6 — Identificação de Pontos Críticos e Condição Inicial')
ax.set_xlabel('Tempo (ms)')
ax.set_ylabel('Corrente i(t) (mA)')
ax.legend(loc='upper right')
plt.tight_layout()
plt.show()


# Q7: Representação visual das formas de onda 7(a) e 7(b)
t_a_ms = np.linspace(-0.25, 0.75, 800)
v_a_mv = 6.0 * np.sin(4000 * np.pi * (t_a_ms/1000) + np.radians(30))

t_b_ms = np.linspace(-10, 25, 800)
i_b_ma = 20.0 * np.sin(120 * np.pi * (t_b_ms/1000) - np.radians(60))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
ax1.plot(t_a_ms, v_a_mv, color='#2980b9', lw=2)
ax1.axhline(0, color='black', lw=0.6)
ax1.axvline(0, color='black', lw=0.6)
ax1.set_title(r'7(a): $v(t) = 6\sin(4000\pi t + 30^\circ)\ \mathrm{mV}$')
ax1.set_xlabel('Tempo (ms)')
ax1.set_ylabel('Tensão (mV)')

ax2.plot(t_b_ms, i_b_ma, color='#e67e22', lw=2)
ax2.axhline(0, color='black', lw=0.6)
ax2.axvline(0, color='black', lw=0.6)
ax2.set_title(r'7(b): $i(t) = 20\sin(120\pi t - 60^\circ)\ \mathrm{mA}$')
ax2.set_xlabel('Tempo (ms)')
ax2.set_ylabel('Corrente (mA)')

plt.tight_layout()
plt.show()


# Q8: Teste de consistência trigonométrica
theta_grid = np.linspace(0, 2*np.pi, 600)
diff_a = np.max(np.abs(10*np.sin(theta_grid + np.radians(30)) - 10*np.cos(theta_grid - np.radians(60))))
diff_b = np.max(np.abs(-9*np.sin(theta_grid) - 9*np.cos(theta_grid + np.radians(90))))
diff_c = np.max(np.abs(-20*np.sin(theta_grid + np.radians(45)) - 20*np.cos(theta_grid + np.radians(135))))

print("--- Resolução da Questão 8 (Validação de Erro Residual) ---")
print(f"Erro máximo Item a: {diff_a:.2e}")
print(f"Erro máximo Item b: {diff_b:.2e}")
print(f"Erro máximo Item c: {diff_c:.2e}")


# Q9: Comparação fasorial e gráficos de defasagem
t_q9 = np.linspace(0, np.pi, 600)
x_t = 13*np.cos(2*t_q9) + 5*np.sin(2*t_q9)
y_t = 15*np.cos(2*t_q9 - np.radians(11.8))

fig, ax = plt.subplots(figsize=(9, 3.8))
ax.plot(t_q9, x_t, color='#2c3e50', lw=2, label='x(t) = 13 cos(2t) + 5 sen(2t)')
ax.plot(t_q9, y_t, color='#d35400', lw=2, ls='--', label='y(t) = 15 cos(2t - 11.8 deg)')
ax.set_title('Questão 9(c) — Comparação Temporal: y(t) Adiantada por 9.24 graus')
ax.set_xlabel('Tempo (s)')
ax.set_ylabel('Amplitude')
ax.legend(loc='upper right')
plt.tight_layout()
plt.show()


# Q10: Plotagem da defasagem V e I
t10 = np.linspace(0, 2*np.pi/377, 800)
v_sinal = 10 * np.cos(377*t10 + np.radians(30))
i_sinal = 5 * np.sin(377*t10 - np.radians(20))

fig, ax = plt.subplots(figsize=(9, 3.8))
ax.plot(t10*1000, v_sinal, color='#16a085', lw=2, label='v(t) = 10 cos(377t + 30 deg) V')
ax.plot(t10*1000, i_sinal, color='#c0392b', lw=2, ls='--', label='i(t) = 5 sen(377t - 20 deg) A')
ax.set_title('Questão 10 — Relação de Fase: v(t) Adianta i(t) em 140 graus')
ax.set_xlabel('Tempo (ms)')
ax.set_ylabel('Amplitude')
ax.legend(loc='upper right')
plt.tight_layout()
plt.show()


# Q11: Demonstração da periodicidade composta
p_val = 3.14
T0_q11 = 100 * np.pi

t_q11 = np.linspace(0, T0_q11, 2500)
v_q11 = np.cos(t_q11) + np.cos(2 * p_val * t_q11)

fig, ax = plt.subplots(figsize=(10, 3.8))
ax.plot(t_q11, v_q11, color='#8e44ad', lw=1.2)
ax.set_title(f'Questão 11 — Forma de Onda com Período Fundamental T0 = 100*pi ~= {T0_q11:.2f} s')
ax.set_xlabel('Tempo t (s)')
ax.set_ylabel('v(t) (V)')
plt.tight_layout()
plt.show()


# Q12: Verificação do período e identidade
t_12 = np.linspace(0, 2*np.pi, 800)
v12_a = np.cos(5*t_12) * np.sin(3*t_12 + np.radians(45))
v12_b = 0.5 * np.cos(8*t_12 - np.radians(45)) + 0.5 * np.cos(2*t_12 + np.radians(45))

print("--- Resolução da Questão 12 ---")
print(f"Erro máximo da decomposição: {np.max(np.abs(v12_a - v12_b)):.2e}")
print(f"Período fundamental T0 = pi ~= {np.pi:.4f} s")


# Q13: Cálculos e resumo
Vm13 = 25.0
w13 = 400 * np.pi
f13 = 200.0
T13_ms = 5.0
t_zero13 = (1.0 / 2400.0) * 1000
dt_i = (7.0 / 2400.0) * 1000

print("--- Resolução da Questão 13 ---")
print(f"(a) Vm = {Vm13} V | (b) f = {f13} Hz | (c) omega = {w13:.2f} rad/s")
print(f"(d) phi = {np.pi/3:.4f} rad | (e) phi = 60° | (f) T = {T13_ms} ms")
print(f"(g) Primeiro zero: {t_zero13:.4f} ms")
print(f"(h) v_deslocada = 25 cos(400*pi*t) V")
print(f"(i) Deslocamento mínimo: {dt_i:.4f} ms")


# Q14: Validação de derivada e expressão
w14 = 750 * np.pi / 50.0
phi14_deg = np.degrees(w14 * 40.0 / 3000.0)

print("--- Resolução da Questão 14 ---")
print(f"(a) omega = {w14:.2f} rad/s ({w14/np.pi:.1f}*pi rad/s)")
print(f"(b) v(t) = 50 sen({w14/np.pi:.1f}*pi*t - {phi14_deg:.1f}°) V")


# Q15: Gráfico reconstruído da questão 15
t_q15 = np.linspace(-3, 13, 1000)
v_q15 = 24.0 * np.cos((500*np.pi/3) * (t_q15/1000) + np.radians(60))

fig, ax = plt.subplots(figsize=(9, 3.8))
ax.plot(t_q15, v_q15, color='#2980b9', lw=2, label='v(t) = 24 cos(500*pi/3 * t + 60 deg) V')
ax.plot([0, 2, 5, 11], [12, 0, -24, 24], 'ro')
for t_val, v_val in zip([0, 2, 5, 11], [12, 0, -24, 24]):
    ax.annotate(f'({t_val} ms, {v_val} V)', (t_val, v_val), textcoords="offset points", xytext=(0,8), ha='center', fontsize=8)
ax.set_title('Questão 15 — Forma de Onda Cosseno Ajustada aos Pontos Experimentais')
ax.set_xlabel('Tempo (ms)')
ax.set_ylabel('Tensão (V)')
ax.legend(loc='upper right')
plt.tight_layout()
plt.show()


# Q16: Simulação
t16 = np.linspace(0, 40, 1000)
v16 = 10 * np.sin(2 * np.pi * t16 / 20)
print("--- Resolução da Questão 16 ---")
print(f"(a) Vp = 10 V | (b) v(15ms) = {v16[t16>=15][0]:.1f} V, v(20ms) = {v16[t16>=20][0]:.1f} V")
print("(c) Vpp = 20 V | (d) T = 20 ms | (e) N = 2 ciclos")


# Q17: Integração por degraus
area_17 = 6*(10-5) + 3*(20-10) + (-3)*(30-20)
T_17 = 30.0
V_med_17 = area_17 / T_17
print(f"Questão 17 -> Área líquida = {area_17} V.ms | Valor Médio = {V_med_17:.2f} V")


# Q18: Cálculo geométrico
area_total_18 = 0.5 * 3 * 30 + 0.5 * 2 * (-20)
I_med_18 = area_total_18 / 7.0
print(f"Questão 18 -> Área total = {area_total_18} mA.ms | I_méd = {I_med_18:.4f} mA")


# Q19: Estruturação com Pandas para exibir a tabela de amostras
dados_x = np.array([2, 4, 11, 5, 7, 6, 9, 10, 3, 6, 8, 4, 1, 3, 5])
df_amostras = pd.DataFrame({'n': range(len(dados_x)), 'x(n)': dados_x, 'x^2(n)': dados_x**2})

media_q19 = df_amostras['x(n)'].mean()
rms_q19 = np.sqrt((df_amostras['x^2(n)']).mean())

print("--- Resolução da Questão 19 ---")
print(f"Média amostral: {media_q19:.2f}")
print(f"RMS amostral:   {rms_q19:.4f}")


# Q20: Verificação teórica
print("--- Resolução da Questão 20 ---")
print("Valor Médio = Vm / pi ~= 0.3183 Vm")
print("Valor RMS   = Vm / 2  = 0.5000 Vm")


# Q21: Valores RMS
print("--- Resolução da Questão 21 ---")
print(f"Item a: V_rms = {120/np.sqrt(2):.4f} V")
print(f"Item b: I_rms = {6e-3/np.sqrt(2)*1e3:.4f} mA")
print(f"Item c: V_rms = {8e-6/np.sqrt(2)*1e6:.4f} uV")


# Q22: Integração da rampa e patamares
V_med_22 = 44.0 / 12.0
V_rms_22 = np.sqrt((256.0/3.0 + 256.0 + 8.0) / 12.0)
print(f"Questão 22 -> V_méd = 11/3 = {V_med_22:.4f} V | V_rms = sqrt(262)/3 = {V_rms_22:.4f} V")


# Q23: RMS de sinais compostos
print("--- Resolução da Questão 23 ---")
print(f"(a) I_rms = 10.0 A")
print(f"(b) V_rms = sqrt(16 + 4.5) = {np.sqrt(20.5):.4f} V")
print(f"(c) I_rms = sqrt(64 + 18)  = {np.sqrt(82):.4f} A")
print(f"(d) V_rms = sqrt(41/2)     = {np.sqrt(20.5):.4f} V")


# Q24: Potência na onda triangular
I_rms_24 = 16.0 / np.sqrt(3)
P_24 = 9.0 * (I_rms_24**2)
print(f"Questão 24 -> I_rms = {I_rms_24:.4f} A | Potência Dissipada P = {P_24:.1f} W")


# Q25: Potência onda completa
V_rms_25 = 100.0 / np.sqrt(2)
P_25 = (V_rms_25**2) / 6.0
print(f"Questão 25 -> V_rms = {V_rms_25:.4f} V | Potência P = {P_25:.2f} W (2500/3 W)")


# Q26: Tensão de pico da rede
Vm_26 = 240.0 * np.sqrt(2)
print(f"Questão 26 -> Tensão Máxima Vm = {Vm_26:.2f} V")


# Q27: Meia onda
print("Questão 27 -> V_rms = Vm / 2 = 0.5 * Vm")


# Q28: Corrente eficaz dente-de-serra
I_rms_28 = 20.0 / np.sqrt(3)
print(f"Questão 28 -> I_rms = 20/sqrt(3) = {I_rms_28:.4f} A")


# Q29: Determinação de R
R_29 = 1280.0 / (400.0 / 3.0)
print(f"Questão 29 -> Resistor R = {R_29:.2f} ohms")


# Q30: Pulso retangular
V_rms_30 = np.sqrt(20.0)
print(f"Questão 30 -> V_rms = sqrt(20) = {V_rms_30:.4f} V")


