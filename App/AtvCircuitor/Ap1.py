# -*- coding: utf-8 -*-
# Atividade Teórica T1 — Lista de Exercícios: Senóides
# Aluno: José Gutemberg Cavalcante Melo
# Matrícula: 2215180015
# Disciplina: Circuitos Elétricos II (Circuitos 2)

# Importação de bibliotecas para cálculo numérico e gráficos
import numpy as np
import matplotlib.pyplot as plt

# Configurações de estilo dos gráficos
plt.rcParams['figure.figsize'] = (10, 4.5)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.6
plt.rcParams['grid.linestyle'] = '--'


# Questão 1: Cálculo dos Períodos
freqs = {
    'a': ('200 Hz', 200),
    'b': ('40 MHz', 40e6),
    'c': ('20 kHz', 20e3),
    'd': ('1 Hz', 1)
}

print("=== Questão 1: Períodos ===")
for item, (desc, f) in freqs.items():
    T = 1.0 / f
    if T >= 1:
        print(f"Item {item}) f = {desc:<8} => T = {T:.4f} s")
    elif T >= 1e-3:
        print(f"Item {item}) f = {desc:<8} => T = {T*1e3:.4f} ms ({T} s)")
    elif T >= 1e-6:
        print(f"Item {item}) f = {desc:<8} => T = {T*1e6:.4f} us ({T} s)")
    else:
        print(f"Item {item}) f = {desc:<8} => T = {T*1e9:.4f} ns ({T} s)")


# Questão 2: Tempo para 5 ciclos
f = 1000.0  # 1 kHz
T = 1.0 / f
t_5_ciclos = 5 * T

print("=== Questão 2 ===")
print(f"Frequência: {f} Hz")
print(f"Período de 1 ciclo: {T} s ({T*1000:.1f} ms)")
print(f"Tempo para completar 5 ciclos: {t_5_ciclos} s ({t_5_ciclos*1000:.1f} ms)")

# Simulação gráfica de 5 ciclos
t = np.linspace(0, t_5_ciclos, 1000)
v = np.sin(2 * np.pi * f * t)
plt.figure()
plt.plot(t * 1000, v, 'b-', label='Sinal f = 1 kHz')
plt.axvline(x=t_5_ciclos*1000, color='r', linestyle='--', label=f'5 ciclos = {t_5_ciclos*1000:.1f} ms')
for k in range(1, 6):
    plt.axvline(x=k*T*1000, color='gray', linestyle=':', alpha=0.5)
plt.title('Questão 2: 5 ciclos de onda senoidal de 1 kHz')
plt.xlabel('Tempo (ms)')
plt.ylabel('Amplitude')
plt.legend()
plt.show()


# Questão 3: Velocidade Angular
periodos = {
    'a': ('1.8 s', 1.8),
    'b': ('0.3 ms', 0.3e-3),
    'c': ('8 us', 8e-6),
    'd': ('4 x 10^-6 s', 4e-6)
}

print("=== Questão 3: Velocidade Angular (omega = 2*pi/T) ===")
for item, (desc, T) in periodos.items():
    w = 2 * np.pi / T
    print(f"Item {item}) T = {desc:<14} => omega = {w:.4f} rad/s ({w/np.pi:.2f}*pi rad/s)")


# Questão 4: Amplitude e Frequência
funcoes_q4 = [
    ('a', '20 sen(377t)', 20, 377),
    ('b', '12 sen(2*pi*120t)', 12, 2 * np.pi * 120),
    ('c', '10^6 sen(10.000t)', 1e6, 10000),
    ('d', '-8 sen(10.058t)', 8, 10058)
]

print("=== Questão 4: Amplitude e Frequência ===")
for item, expr, A, w in funcoes_q4:
    f = w / (2 * np.pi)
    print(f"Item {item}) {expr:<22} => Amplitude = {A:.1e} (ou {A}), Frequência = {f:.2f} Hz")


# Questão 5: Período e Frequência de i(t) = 5 cos(400t - 120°)
w = 400.0
f = w / (2 * np.pi)
T = 1.0 / f

print("=== Questão 5 ===")
print(f"Frequência angular: {w} rad/s")
print(f"Frequência (f): {f:.4f} Hz")
print(f"Período (T): {T*1000:.4f} ms ({T:.6f} s)")

# Simulação gráfica de 2 períodos
t = np.linspace(0, 2*T, 1000)
i_t = 5 * np.cos(w * t - np.radians(120))

plt.figure()
plt.plot(t*1000, i_t, 'g-', lw=2, label=r'$i(t) = 5\cos(400t - 120^\circ)$ A')
plt.title('Questão 5: Corrente Senoidal $i(t)$')
plt.xlabel('Tempo (ms)')
plt.ylabel('Corrente (A)')
plt.axhline(0, color='k', lw=0.5)
plt.legend()
plt.show()


# Questão 6: Análise completa de i(t) = 125 cos(800t + 36.87°) mA
Im = 125.0
w = 800.0
phi_deg = 36.87
phi_rad = np.radians(phi_deg)

f = w / (2 * np.pi)
T_ms = (1.0 / f) * 1000
i_0 = Im * np.cos(phi_rad)

# (f) i = 0 => 800t + phi = pi/2
t_zero_ms = ((np.pi/2 - phi_rad) / w) * 1000

# (g) di/dt = 0 => 800t + phi = pi (primeiro pico negativo após t=0)
t_extremo_ms = ((np.pi - phi_rad) / w) * 1000

print("=== Questão 6: Resultados ===")
print(f"(a) Frequência (f): {f:.2f} Hz")
print(f"(b) Período (T): {T_ms:.3f} ms")
print(f"(c) Amplitude máxima (Im): {Im:.1f} mA")
print(f"(d) i(0): {i_0:.2f} mA")
print(f"(e) Fase (phi): {phi_deg:.2f} graus = {phi_rad:.4f} rad")
print(f"(f) Menor t > 0 para i(t) = 0: {t_zero_ms:.4f} ms")
print(f"(g) Menor t > 0 para di/dt = 0: {t_extremo_ms:.4f} ms")

# Gráfico
t_axis = np.linspace(0, T_ms, 1000)
i_vals = Im * np.cos(w * (t_axis/1000) + phi_rad)

plt.figure()
plt.plot(t_axis, i_vals, 'b-', lw=2, label=r'$i(t) = 125\cos(800t + 36.87^\circ)$ mA')
plt.plot(0, i_0, 'ro', label=f'i(0) = {i_0:.1f} mA')
plt.plot(t_zero_ms, 0, 'go', label=f'i(t)=0 em {t_zero_ms:.3f} ms')
plt.plot(t_extremo_ms, -Im, 'mo', label=f'di/dt=0 (mínimo) em {t_extremo_ms:.3f} ms')
plt.axhline(0, color='k', lw=0.5)
plt.title('Questão 6: Forma de Onda e Pontos Notáveis')
plt.xlabel('Tempo (ms)')
plt.ylabel('Corrente (mA)')
plt.legend()
plt.show()


# Questão 7: Simulação das curvas da Figura (a) e (b)
t_a = np.linspace(-0.25e-3, 0.75e-3, 1000)
v_a = 6 * np.sin(4000 * np.pi * t_a + np.radians(30))

t_b = np.linspace(-10e-3, 25e-3, 1000)
i_b = 20 * np.sin(120 * np.pi * t_b - np.radians(60))

fig, axs = plt.subplots(1, 2, figsize=(13, 4.5))

axs[0].plot(t_a*1000, v_a, 'b-', lw=2, label=r'$v(t) = 6\sin(4000\pi t + 30^\circ)$ mV')
axs[0].set_title('Questão 7(a): Forma de Onda v(t)')
axs[0].set_xlabel('Tempo (ms)')
axs[0].set_ylabel('Tensão (mV)')
axs[0].axhline(0, color='k', lw=0.5)
axs[0].axvline(0, color='k', lw=0.5)
axs[0].legend()

axs[1].plot(t_b*1000, i_b, 'r-', lw=2, label=r'$i(t) = 20\sin(120\pi t - 60^\circ)$ mA')
axs[1].set_title('Questão 7(b): Forma de Onda i(t)')
axs[1].set_xlabel('Tempo (ms)')
axs[1].set_ylabel('Corrente (mA)')
axs[1].axhline(0, color='k', lw=0.5)
axs[1].axvline(0, color='k', lw=0.5)
axs[1].legend()

plt.tight_layout()
plt.show()


# Questão 8: Verificação de equivalência trigonométrica
wt = np.linspace(0, 2*np.pi, 500)

# a. 10 sin(wt + 30°) vs 10 cos(wt - 60°)
f_a1 = 10 * np.sin(wt + np.radians(30))
f_a2 = 10 * np.cos(wt - np.radians(60))

# b. -9 sin(8t) vs 9 cos(8t + 90°)
f_b1 = -9 * np.sin(wt)
f_b2 = 9 * np.cos(wt + np.radians(90))

# c. -20 sin(wt + 45°) vs 20 cos(wt + 135°)
f_c1 = -20 * np.sin(wt + np.radians(45))
f_c2 = 20 * np.cos(wt + np.radians(135))

print("=== Questão 8: Erro máximo de equivalência ===")
print("Erro item a:", np.max(np.abs(f_a1 - f_a2)))
print("Erro item b:", np.max(np.abs(f_b1 - f_b2)))
print("Erro item c:", np.max(np.abs(f_c1 - f_c2)))
print("-> Todas as formas em cosseno foram verificadas e são idênticas!")


# Questão 9: Comparação visual dos pares de senoides
t = np.linspace(0, 2*np.pi/4, 500)
v9a = 10 * np.cos(4*t - np.radians(60))
i9a = 4 * np.sin(4*t + np.radians(50))

plt.figure(figsize=(10, 4))
plt.plot(t, v9a, 'b-', label=r'$v(t) = 10\cos(4t - 60^\circ)$')
plt.plot(t, i9a, 'r--', label=r'$i(t) = 4\sin(4t + 50^\circ) = 4\cos(4t - 40^\circ)$')
plt.title(r'Questão 9(a): $i(t)$ está adiantada por $20^\circ$ em relação a $v(t)$')
plt.xlabel('Tempo (s)')
plt.ylabel('Amplitude')
plt.legend()
plt.show()


# Questão 10: Relação de fase
t = np.linspace(0, 2*np.pi/377, 1000)
v10 = 10 * np.cos(377*t + np.radians(30))
i10 = 5 * np.sin(377*t - np.radians(20))

plt.figure()
plt.plot(t*1000, v10, 'b-', label=r'$v(t) = 10\cos(377t + 30^\circ)$ V')
plt.plot(t*1000, i10, 'r--', label=r'$i(t) = 5\sin(377t - 20^\circ)$ A')
plt.title(r'Questão 10: Defasagem de $140^\circ$ ($v(t)$ adianta $i(t)$)')
plt.xlabel('Tempo (ms)')
plt.ylabel('Amplitude')
plt.legend()
plt.show()


# Questão 11: Período composto
p = 3.14
w1 = 1.0
w2 = 2 * p
T1 = 2 * np.pi / w1
T2 = 2 * np.pi / w2

T0 = 50 * T1  # 100*pi

print("=== Questão 11 ===")
print(f"T1 = {T1:.4f} s, T2 = {T2:.4f} s")
print(f"Período fundamental T0 = 100*pi ~= {T0:.4f} s")

# Simulação gráfica mostrando a periodicidade em T0
t = np.linspace(0, T0, 2000)
v11 = np.cos(t) + np.cos(2*p*t)

plt.figure(figsize=(11, 4))
plt.plot(t, v11, 'm-')
plt.title(f'Questão 11: $v(t) = \cos(t) + \cos(6.28t)$ com Período $T_0 = 100\pi \approx {T0:.2f}$ s')
plt.xlabel('Tempo (s)')
plt.ylabel('v(t)')
plt.show()


# Questão 12: Verificação da decomposição e período
t = np.linspace(0, 2*np.pi, 1000)
v_orig = np.cos(5*t) * np.sin(3*t + np.radians(45))
v_decomp = 0.5 * np.cos(8*t - np.radians(45)) + 0.5 * np.cos(2*t + np.radians(45))

print("=== Questão 12 ===")
print("Erro máximo entre produto e soma de cossenos:", np.max(np.abs(v_orig - v_decomp)))
print(f"Período fundamental T0 = pi ~= {np.pi:.4f} s")

plt.figure()
plt.plot(t, v_orig, 'b-', lw=2, label='v(t) original')
plt.plot(t, v_decomp, 'r--', lw=2, label='0.5 cos(8t - 45°) + 0.5 cos(2t + 45°)')
plt.axvline(np.pi, color='g', linestyle=':', label='T = pi ~= 3.14 s')
plt.title('Questão 12: Decomposição e Período de $v(t)$')
plt.xlabel('Tempo (s)')
plt.ylabel('Amplitude')
plt.legend()
plt.show()


# Questão 13: Cálculo e gráficos
Vm = 25.0
w = 400 * np.pi
f = w / (2 * np.pi)
T_ms = (1 / f) * 1000
phi_deg = 60.0
phi_rad = np.radians(phi_deg)

t_zero_ms = ((np.pi/2 - phi_rad) / w) * 1000
dt_h_ms = 5.0 / 6.0
dt_i_ms = (np.radians(210) / w) * 1000

print("=== Questão 13 ===")
print(f"(a) Vm = {Vm} V")
print(f"(b) f = {f:.1f} Hz")
print(f"(c) omega = {w:.2f} rad/s")
print(f"(d) phi = {phi_rad:.4f} rad")
print(f"(e) phi = {phi_deg} graus")
print(f"(f) T = {T_ms:.1f} ms")
print(f"(g) Primeiro zero após t=0: {t_zero_ms:.4f} ms")
print(f"(h) Expressão deslocada: 25 cos(400*pi*t) V")
print(f"(i) Deslocamento mínimo à esquerda: {dt_i_ms:.4f} ms")

# Gráfico
t_ax = np.linspace(0, 10, 1000)
v_orig = Vm * np.cos(w * (t_ax/1000) + phi_rad)
v_desl_h = Vm * np.cos(w * (t_ax/1000))
v_desl_i = Vm * np.sin(w * (t_ax/1000))

plt.figure(figsize=(11, 4.5))
plt.plot(t_ax, v_orig, 'b-', label=r'Original: $25\cos(400\pi t + 60^\circ)$')
plt.plot(t_ax, v_desl_h, 'g--', label=r'Item h: $25\cos(400\pi t)$')
plt.plot(t_ax, v_desl_i, 'r:', label=r'Item i: $25\sin(400\pi t)$')
plt.title('Questão 13: Tensão Senoidal e Transformações')
plt.xlabel('Tempo (ms)')
plt.ylabel('Tensão (V)')
plt.legend()
plt.show()


# Questão 14: Cálculo e gráfico
Vm = 50.0
dv_dt = 750 * np.pi
w = dv_dt / Vm
t0 = 40.0 / 3000.0  # segundos
phi_rad = w * t0
phi_deg = np.degrees(phi_rad)

print("=== Questão 14 ===")
print(f"(a) Frequência angular omega = {w:.2f} rad/s ({w/np.pi:.1f}*pi rad/s)")
print(f"(b) v(t) = {Vm:.0f} sen({w/np.pi:.1f}*pi*t - {phi_deg:.0f} graus) V")

t_arr = np.linspace(0, 0.2, 1000)
v14 = Vm * np.sin(w * t_arr - phi_rad)

plt.figure()
plt.plot(t_arr * 1000, v14, 'b-', lw=2, label=r'$v(t) = 50\sin(15\pi t - 36^\circ)$ V')
plt.plot(t0 * 1000, 0, 'ro', label=f'Zero subindo em t = {t0*1000:.2f} ms')
plt.title('Questão 14: Tensão Senoidal')
plt.xlabel('Tempo (ms)')
plt.ylabel('Tensão (V)')
plt.legend()
plt.show()


# Questão 15: Simulação da Figura da Questão 15
Vm = 24.0
T_ms = 12.0
w = 2 * np.pi / (T_ms / 1000)
theta_deg = 60.0

t_ms = np.linspace(-4, 14, 1000)
v15 = Vm * np.cos(w * (t_ms / 1000) + np.radians(theta_deg))

plt.figure()
plt.plot(t_ms, v15, 'b-', lw=2, label=r'$v(t) = 24\cos(\frac{500\pi}{3}t + 60^\circ)$ V')
plt.plot(0, 12, 'ro', label='v(0) = 12 V')
plt.plot(2, 0, 'go', label='v(2) = 0 V')
plt.plot(5, -24, 'mo', label='v(5) = -24 V')
plt.plot(11, 24, 'co', label='v(11) = 24 V')
plt.title('Questão 15: Reconstrução da Forma de Onda')
plt.xlabel('Tempo (ms)')
plt.ylabel('Tensão (V)')
plt.legend()
plt.show()


# Questão 16: Gráfico e respostas
t_q16 = np.linspace(0, 40, 1000)
v_q16 = 10 * np.sin(2 * np.pi * t_q16 / 20)

print("=== Questão 16 ===")
print("(a) Valor de pico: 10 V")
print(f"(b) v(15 ms) = {10*np.sin(2*np.pi*15/20):.1f} V, v(20 ms) = {10*np.sin(2*np.pi*20/20):.1f} V")
print("(c) Valor pico a pico: 20 V")
print("(d) Período T = 20 ms")
print("(e) Ciclos visíveis: 2 ciclos")

plt.figure()
plt.plot(t_q16, v_q16, 'b-', lw=2)
plt.plot(15, -10, 'ro', label='v(15 ms) = -10 V')
plt.plot(20, 0, 'go', label='v(20 ms) = 0 V')
plt.title('Questão 16: Onda Senoidal com 2 Ciclos')
plt.xlabel('Tempo (ms)')
plt.ylabel('Tensão (V)')
plt.legend()
plt.show()


# Questão 17: Cálculo do valor médio e gráfico por partes
def v_onda_q17(t_ms):
    t_mod = t_ms % 30
    if 0 <= t_mod < 5: return 0.0
    elif 5 <= t_mod < 10: return 6.0
    elif 10 <= t_mod < 20: return 3.0
    else: return -3.0

t_arr = np.linspace(0, 40, 2000)
v_arr = np.array([v_onda_q17(t) for t in t_arr])

V_med_17 = 30.0 / 30.0

print(f"=== Questão 17: Valor Médio = {V_med_17:.2f} V ===")

plt.figure()
plt.plot(t_arr, v_arr, 'b-', lw=2, label='Forma de onda v(t)')
plt.axhline(V_med_17, color='r', linestyle='--', label=f'V_méd = {V_med_17:.1f} V')
plt.fill_between(t_arr[t_arr<=30], v_arr[t_arr<=30], alpha=0.2, color='blue')
plt.title('Questão 17: Forma de Onda por Degraus e Valor Médio')
plt.xlabel('Tempo (ms)')
plt.ylabel('Tensão (V)')
plt.legend()
plt.show()


# Questão 18: Onda triangular e valor médio
def i_onda_q18(t_ms):
    t_mod = t_ms % 7
    if 0 <= t_mod < 2:
        return 0.0
    elif 2 <= t_mod <= 7:
        # Reta de (2, 30) a (7, -20)
        return 30.0 - (50.0 / 5.0) * (t_mod - 2)
    return 0.0

t_arr = np.linspace(0, 10, 1000)
i_arr = np.array([i_onda_q18(t) for t in t_arr])

I_med_18 = 25.0 / 7.0

print(f"=== Questão 18: I_méd = {I_med_18:.4f} mA ===")

plt.figure()
plt.plot(t_arr, i_arr, 'b-', lw=2, label='i(t) [mA]')
plt.axhline(I_med_18, color='r', linestyle='--', label=f'I_méd = {I_med_18:.3f} mA')
plt.fill_between(t_arr[t_arr<=7], i_arr[t_arr<=7], alpha=0.2, color='blue')
plt.title('Questão 18: Onda Triangular/Linear e Valor Médio')
plt.xlabel('Tempo (ms)')
plt.ylabel('Corrente (mA)')
plt.legend()
plt.show()


# Questão 19: Estatística amostral
amostras = np.array([2, 4, 11, 5, 7, 6, 9, 10, 3, 6, 8, 4, 1, 3, 5])
N = len(amostras)

x_med = np.mean(amostras)
x_rms = np.sqrt(np.mean(amostras**2))

print("=== Questão 19 ===")
print(f"Número de amostras: {N}")
print(f"Soma dos valores: {np.sum(amostras)}")
print(f"Soma dos quadrados: {np.sum(amostras**2)}")
print(f"Valor Médio = {x_med:.2f}")
print(f"Valor RMS = {x_rms:.4f}")

plt.figure()
plt.stem(range(N), amostras, linefmt='b-', markerfmt='bo', basefmt='k-')
plt.axhline(x_med, color='r', linestyle='--', label=f'Média = {x_med:.2f}')
plt.axhline(x_rms, color='g', linestyle=':', label=f'RMS = {x_rms:.2f}')
plt.title('Questão 19: Amostras Discretas, Média e RMS')
plt.xlabel('Índice da amostra (n)')
plt.ylabel('x(n)')
plt.legend()
plt.show()


# Questão 20: Simulação e integração numérica
Vm = 10.0
T = 1.0
t_arr = np.linspace(-T/4, 3*T/4, 2000)
v_semi = np.where((t_arr >= -T/4) & (t_arr <= T/4), Vm * np.cos(2*np.pi*t_arr/T), 0.0)

v_med_num = np.trapezoid(v_semi, t_arr) / T
v_rms_num = np.sqrt(np.trapezoid(v_semi**2, t_arr) / T)

print("=== Questão 20 ===")
print(f"Teórico: V_méd = Vm/pi = {Vm/np.pi:.4f} V | Numérico = {v_med_num:.4f} V")
print(f"Teórico: V_rms = Vm/2 = {Vm/2:.4f} V   | Numérico = {v_rms_num:.4f} V")

plt.figure()
plt.plot(t_arr, v_semi, 'b-', lw=2, label='Cosseno semi-retificado')
plt.axhline(Vm/np.pi, color='r', linestyle='--', label=r'$V_{méd} = V_m/\pi$')
plt.axhline(Vm/2, color='g', linestyle=':', label=r'$V_{rms} = V_m/2$')
plt.title('Questão 20: Onda Cosseno Semi-retificada')
plt.xlabel('Tempo (t/T)')
plt.ylabel('Tensão (V)')
plt.legend()
plt.show()


# Questão 21: RMS de ondas senoidais
sinais_q21 = [
    ('a', '120 sen(377t + 60°)', 120.0, 'V'),
    ('b', '6x10^-3 sen(2*pi*1000t)', 6e-3, 'A'),
    ('c', '8x10^-6 sen(2*pi*5000t + 30°)', 8e-6, 'V')
]

print("=== Questão 21 ===")
for item, expr, Vm, unit in sinais_q21:
    v_rms = Vm / np.sqrt(2)
    print(f"Item {item}) {expr:<30} => V_rms = {v_rms:.4e} {unit}")


# Questão 22: Simulação da onda por partes
def v_onda_q22(t):
    t_mod = t % 12
    if 0 <= t_mod < 4: return 2.0 * t_mod
    elif 4 <= t_mod < 8: return 8.0
    elif 8 <= t_mod < 10: return -2.0
    else: return 0.0

t_arr = np.linspace(0, 14, 2000)
v_arr = np.array([v_onda_q22(t) for t in t_arr])

V_med_22 = 44.0 / 12.0
V_rms_22 = np.sqrt(262.0 / 9.0)

print(f"=== Questão 22 ===")
print(f"Valor Médio = 11/3 ~= {V_med_22:.4f} V")
print(f"Valor RMS = sqrt(262)/3 ~= {V_rms_22:.4f} V")

plt.figure()
plt.plot(t_arr, v_arr, 'b-', lw=2, label='v(t)')
plt.axhline(V_med_22, color='r', linestyle='--', label=f'V_méd = {V_med_22:.2f} V')
plt.axhline(V_rms_22, color='g', linestyle=':', label=f'V_rms = {V_rms_22:.2f} V')
plt.title('Questão 22: Forma de Onda e Valores Médio/RMS')
plt.xlabel('Tempo (s)')
plt.ylabel('Tensão (V)')
plt.legend()
plt.show()


# Questão 23: Cálculo analítico e verificação numérica
rms_23a = 10.0
rms_23b = np.sqrt(4**2 + 3**2 / 2)
rms_23c = np.sqrt(8**2 + (-6)**2 / 2)
rms_23d = np.sqrt((5**2 + 4**2) / 2)

print("=== Questão 23: Valores RMS ===")
print(f"a) i(t) = 10 A                 => I_rms = {rms_23a:.4f} A")
print(f"b) v(t) = 4 + 3 cos(5t) V      => V_rms = {rms_23b:.4f} V")
print(f"c) i(t) = 8 - 6 sen(2t) A      => I_rms = {rms_23c:.4f} A")
print(f"d) v(t) = 5 sen(t) + 4 cos(t) V => V_rms = {rms_23d:.4f} V")


# Questão 24: Onda triangular e potência
Im = 16.0
R = 9.0
I_rms_24 = Im / np.sqrt(3)
P_24 = R * (I_rms_24**2)

print("=== Questão 24 ===")
print(f"Corrente RMS: {I_rms_24:.4f} A")
print(f"Potência Média dissipada: {P_24:.1f} W")

t_arr = np.linspace(0, 6, 1000)
# Gerando onda triangular periódica
i_tri = Im * (1 - np.abs((t_arr % 2) - 1))

plt.figure()
plt.plot(t_arr, i_tri, 'b-', lw=2, label='i(t) [A]')
plt.axhline(I_rms_24, color='r', linestyle='--', label=f'I_rms = {I_rms_24:.2f} A')
plt.title(f'Questão 24: Onda Triangular e Potência no Resistor (P = {P_24:.0f} W)')
plt.xlabel('Tempo (s)')
plt.ylabel('Corrente (A)')
plt.legend()
plt.show()


# Questão 25: Retificação de onda completa
Vm = 100.0
R = 6.0
V_rms_25 = Vm / np.sqrt(2)
P_25 = (V_rms_25**2) / R

print("=== Questão 25 ===")
print(f"Tensão RMS: {V_rms_25:.4f} V")
print(f"Potência Média dissipada: {P_25:.2f} W (2500/3 W)")

t_arr = np.linspace(0, 3*np.pi, 1000)
v_ret = np.abs(Vm * np.sin(t_arr))

plt.figure()
plt.plot(t_arr, v_ret, 'b-', lw=2, label='v(t) = |100 sen(t)|')
plt.axhline(V_rms_25, color='r', linestyle='--', label=f'V_rms = {V_rms_25:.2f} V')
plt.title(f'Questão 25: Onda Completa Retificada (P = {P_25:.2f} W)')
plt.xlabel('Tempo (s)')
plt.ylabel('Tensão (V)')
plt.legend()
plt.show()


# Questão 26: Valor máximo residencial
V_rms = 240.0
Vm_26 = V_rms * np.sqrt(2)

print("=== Questão 26 ===")
print(f"Tensão Eficaz (V_rms): {V_rms:.1f} V")
print(f"Tensão Máxima (Vm): {Vm_26:.2f} V")


# Questão 27: Retificador de meia-onda
Vm = 100.0
T = 1.0
t_arr = np.linspace(0, 2*T, 1000)
v_meia = np.where((t_arr % T) <= T/2, Vm * np.sin(2*np.pi*(t_arr % T)/T), 0.0)

V_rms_27 = Vm / 2.0

print(f"=== Questão 27 ===")
print(f"V_rms = Vm / 2 = {V_rms_27:.2f} V (para Vm = {Vm:.0f} V)")

plt.figure()
plt.plot(t_arr, v_meia, 'b-', lw=2, label='Retificador de meia-onda')
plt.axhline(V_rms_27, color='r', linestyle='--', label=r'$V_{rms} = V_m / 2$')
plt.title('Questão 27: Sinal Retificado de Meia-Onda')
plt.xlabel('Tempo (t/T)')
plt.ylabel('Tensão (V)')
plt.legend()
plt.show()


# Questão 28: Onda dente-de-serra assimétrica
Im = 20.0
T_ms = 100.0
t1_ms = 80.0

I_rms_28 = Im / np.sqrt(3)

print("=== Questão 28 ===")
print(f"Corrente Máxima Im = {Im} A")
print(f"Corrente Eficaz I_rms = 20/sqrt(3) ~= {I_rms_28:.4f} A")

def i_onda_q28(t_ms):
    t_mod = t_ms % 100
    if t_mod <= 80:
        return (20.0 / 80.0) * t_mod
    else:
        return 20.0 - (20.0 / 20.0) * (t_mod - 80)

t_arr = np.linspace(0, 200, 1000)
i_arr = np.array([i_onda_q28(t) for t in t_arr])

plt.figure()
plt.plot(t_arr, i_arr, 'b-', lw=2, label='i(t) [A]')
plt.axhline(I_rms_28, color='r', linestyle='--', label=f'I_rms = {I_rms_28:.2f} A')
plt.title('Questão 28: Corrente com Subida em 80 ms e Descida em 20 ms')
plt.xlabel('Tempo (ms)')
plt.ylabel('Corrente (A)')
plt.legend()
plt.show()


# Questão 29: Resistência para potência dada
P = 1280.0
I_rms_sq = 400.0 / 3.0
R_29 = P / I_rms_sq

print("=== Questão 29 ===")
print(f"Potência Média: {P} W")
print(f"I_rms^2: {I_rms_sq:.4f} A^2")
print(f"Resistência do Resistor (R): {R_29:.2f} ohms")


# Questão 30: Pulso retangular periódico
def v_onda_q30(t):
    t_mod = t % 5
    return 10.0 if t_mod < 1 else 0.0

t_arr = np.linspace(0, 12, 1000)
v_arr = np.array([v_onda_q30(t) for t in t_arr])

V_rms_30 = np.sqrt(20.0)

print(f"=== Questão 30 ===")
print(f"V_rms = sqrt(20) ~= {V_rms_30:.4f} V")

plt.figure()
plt.plot(t_arr, v_arr, 'b-', lw=2, label='v(t) [V]')
plt.axhline(V_rms_30, color='r', linestyle='--', label=f'V_rms = {V_rms_30:.2f} V')
plt.title('Questão 30: Pulso Retangular Periódico')
plt.xlabel('Tempo (s)')
plt.ylabel('Tensão (V)')
plt.legend()
plt.show()


