"""
Le code est écrit en snake_case
les commentaires sont en français
les noms des variables des fonctions et des constantes sont écrites en français ou en anglais
les caractères d'indentation des boucles sont i k w
"""


# ==============================
# bloc des imports
# ===============================
from machine import Pin, I2C, SPI, ADC
import time
import math
import ssd1306
import utime
import st7789
import vga1_bold_16x16
import vga2_8x8

# ========================================
# bloc configuration matériel
# ========================================
# Petit écran
i2c = I2C(0, scl=Pin(1), sda=Pin(0))
oled_petit = ssd1306.SSD1306_I2C(128, 64, i2c)

# Écran ST7789 sur SPI1 (gros écran)
spi = SPI(
    1,
    baudrate=40_000_000,
    polarity=1,
    phase=1,
    sck=Pin(10),
    mosi=Pin(11),
)

rst = Pin(12, Pin.OUT)
dc  = Pin(13, Pin.OUT)
cs  = Pin(9, Pin.OUT)

tft = st7789.ST7789(
    spi,
    240,
    320,
    reset=rst,
    dc=dc,
    cs=cs,
    rotation=0,
    color_order=st7789.BGR,
)

# Boutons pour raquette gauche (ces boutons servent également au débuggage si des problèmes de voix surviennent)
btn_up = Pin(20, Pin.IN, Pin.PULL_DOWN)
btn_down = Pin(21, Pin.IN, Pin.PULL_DOWN)
btn_debug = Pin(22, Pin.IN, Pin.PULL_DOWN)

# Capteurs
adc_sound = ADC(26)   # Capteur son (GP26)
adc_pulse = ADC(27)   # Capteur pouls (GP27)
led = Pin(19, Pin.OUT)

# ========================================
# bloc des constantes
# ========================================

# constantes pong
difficulte_globale = 0.7  # constante gérant la vitesse de la raquette du bot et de la balle
largeur = 240  # largeur écran
hauteur = 320  # hauteur écran
rayon = 4  # rayon balle
raq_h = 40  # raquette hauteur
raq_w = 6  # raquette largeur
v_raquette = 9  # vitesse de la raquette avec les boutons du débuggage
difficulte_raquette = 2 * difficulte_globale  # vitesse de la raquette du bot
score_victoire = 11
frequence_de_base = 400  # fréquence considérée comme étant celle de base en parlant
bpm_ref = 80  # BPM de référence
largeur_effective = 20  # écart de BPM pour effet max
k_vitesse_bpm = 1.3  # intensité de l'effet
note_names = ["Do", "Do#", "Re", "Re#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si"]


# constantes capteurs
sound_samples = 100  # nombres d'échantillons avant de faire un calcul
sound_delay = 500  # temps d'attentes entre 2 mesures en µs
pulse_threshold = 2000  # valeur de seuil pour faire la mesure
sound_threshold = 350  # valeur de seuil pour qu'on considère un son
cri_threshold = 900  # valeur de seuil pour considérer un cri

# ========================================
# bloc des variables
# ========================================

# Pong
raq1_y = hauteur // 2 - raq_h // 2  # on met au milieu
raq2_y = hauteur // 2 - raq_h // 2  # on met au milieu
bal_x = largeur // 2  # on met au milieu
bal_y = hauteur // 2  # on met au milieu
vx = 3 * difficulte_globale  # vitesse balle x
vy = 2 * difficulte_globale  # vitesse balle y
score_g = 0
score_d = 0
score_diff = 0
remontada = False  # variable qui active un événement si la différence de score est trop faible

start_time = time.ticks_ms()  # compteur de temps

# Barre coup spécial
duree_chargement_ms = 15000  # 15s
barre_largeur_max = 200
barre_hauteur = 8
barre_x = (largeur - barre_largeur_max) // 2
barre_y = 16

# Smash
smash_ready = False
smash_active = False
smash_speed_mult = 2.0  # permet que le smash soit plus ou moins efficace
vx_before_smash = 0.0  # sert à calculer proprement la vitesse de la balle lors du smash
vy_before_smash = 0.0

# Mur - permet de doubler la taille de la raquette
mur_active = False
mur_duree_ms = 12000
mur_debut_ms = 0
mur_mult_h = 2 #multiplicateur de taille
raq1_h_effective = raq_h

# Freeze - permet d'arrêter la raquette adverse
freeze_active = False
freeze_duree_ms = 8000
freeze_debut_ms = 0

# Type de coup spécial actuel
coup_special_actuel = None  # "Smash", "Mur", "Freeze" ou None

# Positions précédentes - permet l'utilisation de plusieurs fonctions notamment celles de contact
prev_raq1_y = raq1_y
prev_raq2_y = raq2_y
prev_bal_x = bal_x
prev_bal_y = bal_y
prev_score_txt = ""

# Capteurs - initialisation globale
sound_intensity = 0.0
sound_frequency = 0
sound_frequency_list = []
heart_rate = 0
heart_rate_list = []
pulse_intervals = []
last_pulse_time = time.ticks_ms()
pulse_beat = False

cycle_count = 0
prev_btn_up = False
prev_btn_down = False
prev_btn_debug = False

# ========================================
# FONCTIONS CAPTEURS
# ========================================

#detecte la fréquence sonore est complémentaire à lire_capteur_son
def detect_frequency(samples, sample_rate):
    if len(samples) < 10:
        return 0
    
    moyenne = sum(samples) / len(samples)
    zero_crossings = 0
    
    for i in range(1, len(samples)):
        if (samples[i-1] < moyenne and samples[i] >= moyenne) or \
           (samples[i-1] >= moyenne and samples[i] < moyenne):
            zero_crossings += 1
    
    duree = len(samples) / sample_rate
    freq = (zero_crossings / 2) / duree
    return int(freq)


#donne l'intensité et la fréquence sonore
def lire_capteur_son():
    global sound_intensity, sound_frequency
    
    buffer = []
    min_val = 65535
    max_val = 0
    
    for _ in range(sound_samples):
        val = adc_sound.read_u16()
        buffer.append(val)
        if val < min_val:
            min_val = val
        if val > max_val:
            max_val = val
        utime.sleep_us(sound_delay)
    
    amplitude = max_val - min_val
    sound_intensity = round(amplitude / 65535, 3) * 1000

    if sound_intensity < sound_threshold:
        sound_frequency = 0
        return
    
    sample_rate = 1000000 / sound_delay
    sound_frequency = detect_frequency(buffer, sample_rate)
    sound_frequency_list.append(sound_frequency)

#donne toutes les informations ressortant du capteur de pouls
def lire_capteur_pouls():
    global heart_rate, pulse_intervals, last_pulse_time, pulse_beat
    
    signal = adc_pulse.read_u16()
    current_time = time.ticks_ms()
    
    if signal > pulse_threshold and not pulse_beat:
        pulse_beat = True
        interval = time.ticks_diff(current_time, last_pulse_time)
        last_pulse_time = current_time
        
        if 300 < interval < 2000:
            pulse_intervals.append(interval)
            if len(pulse_intervals) > 10:
                pulse_intervals.pop(0)
            if len(pulse_intervals) > 2:
                avg_interval = sum(pulse_intervals) / len(pulse_intervals)
                heart_rate = int(60000 / avg_interval)
                heart_rate_list.append(heart_rate)  # peut être source de lag
        led.value(1)
    
    if signal < pulse_threshold and pulse_beat:
        pulse_beat = False
        led.value(0)

#permet le calibrage du pouls
def calibrer_bpm(duree_ms):
    global bpm_ref, heart_rate, heart_rate_list, pulse_intervals, last_pulse_time, pulse_beat
    tft.fill(st7789.BLACK)
    tft.text(vga1_bold_16x16, "Calibration", largeur//2-len("Calibration")//2*16, 100, st7789.WHITE, st7789.BLACK)
    tft.text(vga1_bold_16x16, "BPM", largeur//2-len("BPM")//2*16, 132, st7789.WHITE, st7789.BLACK)

    tft.text(vga1_bold_16x16, "Reste calme...", 20, 164, st7789.WHITE, st7789.BLACK)

    oled_petit.fill(0)
    oled_petit.text("CALIBRATION BPM", 5, 0)
    oled_petit.text("Reste calme", 20, 20)
    oled_petit.text("Ne bouge pas", 15, 35)
    oled_petit.show()

    heart_rate_list = []
    pulse_intervals = []
    last_pulse_time = time.ticks_ms()
    pulse_beat = False

    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < duree_ms:
        lire_capteur_pouls()
        # petit affichage BPM courant si dispo
        oled_petit.fill_rect(0, 50, 128, 14, 0)
        oled_petit.text("BPM: {}".format(heart_rate if heart_rate > 0 else "--"), 35, 50)
        oled_petit.show()
        time.sleep(0.05)

    if heart_rate_list:
        bpm_ref = int(sum(heart_rate_list) / len(heart_rate_list))
    else:
        bpm_ref = 80  # considéré comme rythme de base

    # petit écran de fin de calibration
    tft.fill(st7789.BLACK)
    tft.text(vga1_bold_16x16, "BPM ref: {}".format(bpm_ref), 20, 120, st7789.WHITE, st7789.BLACK)
    oled_petit.fill(0)
    oled_petit.text("CALIB OK", 30, 0)
    oled_petit.text("BPM ref: {}".format(bpm_ref), 10, 20)
    oled_petit.show()
    time.sleep(2)

def calibrer_frequence(duree_ms):
    global frequence_de_base, sound_frequency
    tft.fill(st7789.BLACK)
    tft.text(vga1_bold_16x16, "Calib frequence", 10, 80, st7789.WHITE, st7789.BLACK)
    tft.text(vga1_bold_16x16, "Du grave", 10, 120, st7789.WHITE, st7789.BLACK)
    tft.text(vga1_bold_16x16, "au aigu", 10, 140, st7789.WHITE, st7789.BLACK)

    oled_petit.fill(0)
    oled_petit.text("CALIB FREQUENCE", 0, 0)
    oled_petit.text("Du plus grave", 0, 20)
    oled_petit.text("au plus aigu", 0, 32)
    oled_petit.text("Appuie bouton", 0, 48)
    oled_petit.show()

    mins = []
    maxs = []

    # États initiaux des boutons
    prev_up = btn_up.value()
    prev_down = btn_down.value()
    prev_debug = btn_debug.value()

    while True:
        lire_capteur_son()
        f = sound_frequency

        # On ne garde que des fréquences plausibles
        if 50 < f < 2000:
            # On stocke des valeurs basses et hautes
            # Pour limiter la taille des listes, on tronque à 30 valeurs
            if len(mins) < 30 or f < max(mins):
                mins.append(f)
                mins = sorted(mins)[:30]      # garde les 30 plus petites
            if len(maxs) < 30 or f > min(maxs):
                maxs.append(f)
                maxs = sorted(maxs)[-30:]     # garde les 30 plus grandes

        # feedback visuel
        oled_petit.fill_rect(0, 48, 128, 16, 0)
        oled_petit.text("f: {}Hz".format(int(f)), 0, 48)
        if mins:
            oled_petit.text("min:{:4d}".format(int(sum(mins)/len(mins))), 0, 56)
        if maxs:
            oled_petit.text("max:{:4d}".format(int(sum(maxs)/len(maxs))), 64, 56)
        oled_petit.show()

        # lecture actuelle des boutons
        cur_up = btn_up.value()
        cur_down = btn_down.value()
        cur_debug = btn_debug.value()

        # sortie dès changement d'état sur un bouton
        if cur_up != prev_up or cur_down != prev_down or cur_debug != prev_debug:
            break

        time.sleep(0.05)

    if mins and maxs:
        f_min_moy = sum(mins) / len(mins)
        f_max_moy = sum(maxs) / len(maxs)
        frequence_de_base = int((f_min_moy + f_max_moy) / 2)
    elif maxs:
        frequence_de_base = int(sum(maxs) / len(maxs))
    else:
        frequence_de_base = 400  # considéré comme fréquence de base

    tft.fill(st7789.BLACK)
    tft.text(vga1_bold_16x16, "Freq base:", 10, 100, st7789.WHITE, st7789.BLACK)
    tft.text(vga1_bold_16x16, "{} Hz".format(frequence_de_base), 10, 130, st7789.WHITE, st7789.BLACK)

    oled_petit.fill(0)
    oled_petit.text("CALIB OK", 20, 0)
    oled_petit.text("Freq base:", 5, 20)
    oled_petit.text("{} Hz".format(frequence_de_base), 5, 32)
    oled_petit.show()
    time.sleep(2)

def facteur_vitesse_bpm(bpm):
    # écart absolu par rapport à la référence
    d = abs(bpm - bpm_ref)

    # delta_max = écart où on atteint l'effet max (0.5 -> 2)
    delta_max = 30.0

    # normalisation entre 0 et 1
    x = d / delta_max
    if x > 1.0:
        x = 1.0
    # on accentue encore avec une puissance > 1
    expo = 0.7
    x = x ** expo
    # f varie de f_min à f_max en fonction de x
    f_min = 1
    f_max = 2.5
    f = f_min + (f_max - f_min) * x

    return f

#donne la note en fonction de la fréquence
def freq_to_note(freq):
    if freq <= 0:
        return "Inaudible"
    n = 69 + 12 * math.log(freq/440.0, 2)
    n_round = int(round(n))
    name = note_names[n_round % 12]
    octave = (n_round // 12) - 1
    return f"{name}{octave}"

# affichage petit écran
def afficher_pouls_oled(freq_filtre, note_actuelle):
    oled_petit.fill(0)
    oled_petit.text(f"Score : {score_g}-{score_d}", 10, 0)
    oled_petit.hline(0, 10, 128, 1)
    oled_petit.text("BPM:", 10, 20)
    if heart_rate > 0:
        oled_petit.text(str(heart_rate), 50, 20)
    else:
        oled_petit.text("--", 50, 20)
    if pulse_beat:
        oled_petit.fill_rect(100, 18, 10, 10, 1)
    else:
        oled_petit.rect(100, 18, 10, 10, 1)
    oled_petit.text(f"Son : {int(sound_intensity)}", 10, 31)
    oled_petit.text(f"Freq : {int(freq_filtre)}Hz", 10, 42)
    oled_petit.text(f"Note : {note_actuelle}",   10, 53)
    oled_petit.show()

# ========================================
# FONCTIONS PONG
# ========================================

#si la balle arrive en haut ou en bas de l'écran
def bordure(py, vy):
    if py + rayon >= hauteur:
        vy = -vy
        py = hauteur - rayon - 1
    elif py - rayon <= 0:
        vy = -vy
        py = rayon + 1
    return vy, py

#fonction gérant l'effet de la fréquence sur le mouvement de la raquette
def commande_frequence(freq, freq_basique):
    coeff_reducteur = 8
    if freq < 40:
        return 0
    if freq == freq_basique:
        return 0
    vy = math.log(1 + abs(freq_basique - freq))
    vy = coeff_reducteur * vy * (freq_basique - freq) / abs(freq_basique - freq)
    return vy

# COUPS SPECIAUX
#sert à maj_barre_coup_special()
def reset_barre_coup_special():
    global start_time
    start_time = time.ticks_ms()

#sert à maj_barre_coup_special()
def barre_pleine():
    now = time.ticks_ms()
    elapsed = time.ticks_diff(now, start_time)
    return elapsed >= duree_chargement_ms

# gère tous les coups spéciaux ainsi que le chargement et l'utilisation de la barre des pouvoirs
def maj_barre_coup_special():
    now = time.ticks_ms()
    # Si le gel (freeze) est actif, afficher le temps restant en vidant la barre.
    if freeze_active:
        elapsed_freeze = time.ticks_diff(now, freeze_debut_ms)
        if elapsed_freeze < 0:
            elapsed_freeze = 0
        if elapsed_freeze > freeze_duree_ms:
            elapsed_freeze = freeze_duree_ms
        # fraction restante (1 = plein, 0 = vide)
        frac_remaining = 1.0 - (elapsed_freeze / float(freeze_duree_ms))
        if frac_remaining < 0:
            frac_remaining = 0
        if frac_remaining > 1:
            frac_remaining = 1
        barre_largeur = int(barre_largeur_max * frac_remaining)
        tft.fill_rect(barre_x, barre_y, barre_largeur_max, barre_hauteur, st7789.BLACK)
        # utiliser une couleur distincte pour le décompte du freeze
        tft.fill_rect(barre_x, barre_y, barre_largeur, barre_hauteur, st7789.GREEN)
        return

    if mur_active:
        elapsed_mur = time.ticks_diff(now, mur_debut_ms)
        if elapsed_mur < 0:
            elapsed_mur = 0
        if elapsed_mur > mur_duree_ms:
            elapsed_mur = mur_duree_ms
        # fraction restante (1 → plein, 0 → vide)
        frac_remaining_mur = 1.0 - (elapsed_mur / float(mur_duree_ms))
        if frac_remaining_mur < 0:
            frac_remaining_mur = 0
        if frac_remaining_mur > 1:
            frac_remaining_mur = 1
        barre_largeur = int(barre_largeur_max * frac_remaining_mur)
        tft.fill_rect(barre_x, barre_y, barre_largeur_max, barre_hauteur, st7789.BLACK)
        # utiliser une couleur distincte pour le décompte du freeze
        tft.fill_rect(barre_x, barre_y, barre_largeur, barre_hauteur, st7789.GREEN)
        return
    # Afficher la barre normale de chargement / disponibilité
    elapsed = time.ticks_diff(now, start_time)
    if elapsed < 0:
        elapsed = 0
    if elapsed > duree_chargement_ms:
        elapsed = duree_chargement_ms
    progress = elapsed / duree_chargement_ms
    barre_largeur = int(barre_largeur_max * progress)
    if elapsed < duree_chargement_ms:
        barre_couleur = st7789.WHITE
    else:
        barre_couleur = st7789.RED
    tft.fill_rect(barre_x, barre_y, barre_largeur_max, barre_hauteur, st7789.BLACK)
    tft.fill_rect(barre_x, barre_y, barre_largeur, barre_hauteur, barre_couleur)

# Smash
def smash_disponible():
    # condition pour déclencher Smash (cri)
    return True

# fait l'effet du smash et réinitialises les données associées
def fin_smash():
    global smash_active, smash_ready, vx, vy, vx_before_smash, vy_before_smash, coup_special_actuel
    if smash_active:
        smash_active = False
        smash_ready = False
        if vx_before_smash != 0 or vy_before_smash != 0:
            vx = vx_before_smash
            vy = vy_before_smash
    coup_special_actuel = None
    reset_barre_coup_special()

# Mur
# fait l'effet du mur et réinitialises les données associées
def activer_mur():
    global mur_active, mur_debut_ms, raq1_h_effective, prev_raq1_y
    mur_active = True
    mur_debut_ms = time.ticks_ms()
    # effacer l'ancienne raquette avant d'agrandir
    tft.fill_rect(0, int(raq1_y), raq_w, raq1_h_effective, st7789.BLACK)
    raq1_h_effective = raq_h * mur_mult_h
    prev_raq1_y = -1  # force redraw

def fin_mur():
    global mur_active, raq1_h_effective, coup_special_actuel, prev_raq1_y
    if mur_active:
        # effacer l'ancienne grande raquette
        tft.fill_rect(0, int(raq1_y), raq_w, raq1_h_effective, st7789.BLACK)
        mur_active = False
        raq1_h_effective = raq_h
        prev_raq1_y = -1
    coup_special_actuel = None
    reset_barre_coup_special()

def maj_mur_temps():
    if not mur_active:
        return
    now = time.ticks_ms()
    if time.ticks_diff(now, mur_debut_ms) > mur_duree_ms:
        fin_mur()

# Freeze
# fait l'effet du freeze et réinitialises les données associées
def activer_freeze():
    global freeze_active, freeze_debut_ms
    freeze_active = True
    freeze_debut_ms = time.ticks_ms()

def fin_freeze():
    global freeze_active, coup_special_actuel
    if freeze_active:
        freeze_active = False
    coup_special_actuel = None
    reset_barre_coup_special()

def maj_freeze_temps():
    if not freeze_active:
        return
    now = time.ticks_ms()
    if time.ticks_diff(now, freeze_debut_ms) > freeze_duree_ms:
        fin_freeze()

def effacer_balle(x, y):
    erase_margin = 5
    x0 = int(x - rayon - erase_margin)
    y0 = int(y - rayon - erase_margin)
    w = rayon*2 + 2*erase_margin
    h = rayon*2 + 2*erase_margin
    if x0 < 0:
        x0 = 0
    if y0 < 0:
        y0 = 0
    if x0 + w > largeur:
        w = largeur - x0
    if y0 + h > hauteur:
        h = hauteur - y0
    tft.fill_rect(x0, y0, w, h, st7789.BLACK)


#affiche les différents éléments du jeu
def maj_affichage_jeu():
    global prev_raq1_y, prev_raq2_y, prev_bal_x, prev_bal_y
    # Effacer ancienne raquette gauche
    if prev_raq1_y != raq1_y:
        tft.fill_rect(0, int(prev_raq1_y), raq_w, raq1_h_effective, st7789.BLACK)
    # Effacer ancienne raquette droite
    if prev_raq2_y != raq2_y:
        tft.fill_rect(largeur - raq_w, int(prev_raq2_y), raq_w, raq_h, st7789.BLACK)
    # Effacer ancienne balle
    effacer_balle(prev_bal_x, prev_bal_y)
    # Dessiner nouvelles positions
    tft.fill_rect(0, int(raq1_y), raq_w, raq1_h_effective, st7789.WHITE)
    couleur_raq2 = st7789.BLUE if freeze_active else st7789.WHITE
    tft.fill_rect(largeur - raq_w, int(raq2_y), raq_w, raq_h, couleur_raq2)

    if smash_active:
        # Smash prioritaire: balle pleine rouge
        tft.fill_rect(int(bal_x - rayon), int(bal_y - rayon), rayon * 2, rayon * 2, st7789.RED)
    else:
        # Affichage type BPM petit écran:
        # - pas de battement: balle pleine blanche
        # - battement détecté: balle vide (contour blanc)
        if pulse_beat:
            # balle vide: on efface l'intérieur et on dessine juste le contour
            tft.fill_rect(int(bal_x - rayon), int(bal_y - rayon), rayon * 2, rayon * 2, st7789.BLACK)
            tft.rect(int(bal_x - rayon), int(bal_y - rayon), rayon * 2, rayon * 2, st7789.WHITE)
        else:
            # balle pleine
            tft.fill_rect(int(bal_x - rayon), int(bal_y - rayon), rayon * 2, rayon * 2, st7789.WHITE)

    prev_raq1_y = raq1_y
    prev_raq2_y = raq2_y
    prev_bal_x = bal_x
    prev_bal_y = bal_y

#replace la balle après avoir marqué
def reinit_positions_apres_point():
    global bal_x, bal_y, vx, vy, prev_bal_x, prev_bal_y, coup_special_actuel
    tft.fill(st7789.BLACK)
    bal_x, bal_y = largeur // 2, hauteur // 2
    if score_d > score_g:
        vx, vy = (3 * difficulte_globale, 2 * difficulte_globale)
    else:
        vx, vy = (-3 * difficulte_globale, -2 * difficulte_globale)
    prev_bal_x, prev_bal_y = bal_x, bal_y
    fin_smash()
    fin_mur()
    fin_freeze()
    coup_special_actuel = None
    tft.text(vga1_bold_16x16, f"{score_g}-{score_d}", largeur//2-20, 4, st7789.WHITE, st7789.BLACK)
    tft.fill_rect(int(bal_x - rayon), int(bal_y - rayon), rayon * 2, rayon * 2, st7789.WHITE)

# ========================================
# BOUCLE PRINCIPALE
# ========================================

print("=== Pong + Capteurs sur ST7789 ===")
print("\nIntensité | Fréquence (Hz) | BPM | Score")
print("-" * 50)

# Phase de calibrage
calibrer_bpm(duree_ms=20000)
calibrer_frequence(duree_ms=10000)

tft.fill(st7789.BLACK)
tft.fill_rect(0, int(raq1_y), raq_w, raq_h, st7789.WHITE)
tft.fill_rect(largeur - raq_w, int(raq2_y), raq_w, raq_h, st7789.WHITE)
tft.fill_rect(int(bal_x - rayon), int(bal_y - rayon), rayon * 2, rayon * 2, st7789.WHITE)

# ====================
#boucle principale du jeu
# ====================

while score_d < score_victoire and score_g < score_victoire:
    if cycle_count % 10 == 0:
        lire_capteur_son()
    lire_capteur_pouls()
    afficher_pouls_oled(sound_frequency, freq_to_note(sound_frequency))
    # lit les boutons 
    cur_btn_up = btn_up.value()
    cur_btn_down = btn_down.value()
    cur_btn_debug = btn_debug.value()
    
    score_diff = score_g - score_d
    if score_diff < -3:
        remontada = True

    # Choix du pouvoir une fois la barre pleine (rising-edge detection)
    if barre_pleine() and (coup_special_actuel is None):
        # Nécessite une pression pour sélectionner la puissance.
        if cur_btn_debug and not prev_btn_debug:
            coup_special_actuel = "Smash"
        elif cur_btn_down and not prev_btn_down:
            coup_special_actuel = "Mur"
        elif cur_btn_up and not prev_btn_up:
            coup_special_actuel = "Freeze"
        # Activation du pouvoir choisi (reset charge when chosen)
        if coup_special_actuel == "Smash":
            smash_ready = True
            reset_barre_coup_special()
        elif coup_special_actuel == "Mur":
            activer_mur()
            reset_barre_coup_special()
        elif coup_special_actuel == "Freeze":
            activer_freeze()
            reset_barre_coup_special()

    # Durées Mur / Freeze
    maj_mur_temps()
    maj_freeze_temps()

    # Affichage du nom du pouvoir
    tft.fill_rect(0, barre_y + barre_hauteur + 2, largeur, 16, st7789.BLACK)
    # Affichage du nom de la puissance que si elle est à la fois sélectionnée ET que la barre est pleine
    if coup_special_actuel is not None and barre_pleine():
        txt = coup_special_actuel
    else:
        txt = "Chargement..."
    tft.text(
        vga1_bold_16x16,
        txt,
        largeur // 2 - len(txt) * 8,
        barre_y + barre_hauteur + 2,
        st7789.WHITE,
        st7789.BLACK,
    )

    # Titre et barre
    tft.text(
        vga1_bold_16x16,
        "Coup special",
        largeur // 2 - len("Coup special") * 8,
        0,
        st7789.WHITE,
        st7789.BLACK,
    )
    maj_barre_coup_special()

    # Entrées joueur
    if btn_up.value():
        raq1_y -= v_raquette
    if btn_down.value():
        raq1_y += v_raquette

    if btn_debug.value():
        dy = commande_frequence(sound_frequency, frequence_de_base)
        if dy > 5:
            dy = 5
        if dy < -5:
            dy = -5
        raq1_y += dy

    if raq1_y < 0:
        raq1_y = 0
    if raq1_y > hauteur - raq1_h_effective:
        raq1_y = hauteur - raq1_h_effective

    
     # --- MOUVEMENT BALLE dépendant du BPM ---
    facteur = facteur_vitesse_bpm(heart_rate)
    prev_x, prev_y = bal_x, bal_y
    bal_x += vx * facteur
    bal_y += vy * facteur
  
    
    # Bordures haut/bas
    vy, bal_y = bordure(bal_y, vy)

    reset_positions = False
    if bal_x + rayon < 0:
        score_d += 1
        reset_positions = True
    elif bal_x - rayon > largeur:
        score_g += 1
        reset_positions = True
    else:
        # collision raquette gauche (avec Mur)
        if vx < 0 and bal_x - rayon <= raq_w and raq1_y <= bal_y <= raq1_y + raq1_h_effective:
            if coup_special_actuel == "Smash" and smash_ready and (not smash_active) and smash_disponible():
                smash_active = True
                smash_ready  = False
                vx_before_smash = vx
                vy_before_smash = vy
                vx *= smash_speed_mult
                vy *= smash_speed_mult
                reset_barre_coup_special()
            vx = -vx
            bal_x = raq_w + rayon

        # collision raquette droite
        if vx > 0 and bal_x + rayon >= largeur - raq_w and raq2_y <= bal_y <= raq2_y + raq_h:
            vx = -vx
            bal_x = largeur - raq_w - rayon
            if smash_active:
                fin_smash()

    if reset_positions:
        reinit_positions_apres_point()

    # IA raquette droite (gelée si Freeze)
    if not freeze_active:
        if bal_y < raq2_y + raq_h / 2:
            raq2_y -= difficulte_raquette 
        elif bal_y > raq2_y + raq_h / 2:
            raq2_y += difficulte_raquette
        raq2_y = max(0, min(hauteur - raq_h, raq2_y))

    maj_affichage_jeu()

    if cycle_count % 50 == 0:
        print(f"  {facteur}   |     {vx}      | {vy} | {score_g}-{score_d}")

    cycle_count += 1
    # mettre à jour les états précédents des boutons pour la détection de front
    prev_btn_up = bool(cur_btn_up)
    prev_btn_down = bool(cur_btn_down)
    prev_btn_debug = bool(cur_btn_debug)
    time.sleep(0.03)
    
tft.fill(st7789.BLACK)
if score_d == score_victoire:
    tft.text(vga1_bold_16x16, "Tu es nul...", largeur//2-len("Tu es nul...")//2*16, 20, st7789.WHITE, st7789.BLACK)
    tft.text(vga1_bold_16x16, "et c'est OK", largeur//2-len("et c'est OK")//2*16, 20+32, st7789.WHITE, st7789.BLACK)

if score_g == score_victoire:
    tft.text(vga1_bold_16x16, "FELICITATIONS", largeur//2-len("FELICITATIONS")//2*16, 20, st7789.WHITE, st7789.BLACK)
    if remontada:
        tft.text(vga1_bold_16x16, "REMONTADAAA!!", largeur//2-len("REMONTADAAA!!")//2*16, 20+32, st7789.WHITE, st7789.BLACK)
    else:
        if score_diff >= 5:
            tft.text(vga1_bold_16x16, "L'IA n'avait", largeur//2-len("L'IA n'avait")//2*16, 20+32, st7789.WHITE, st7789.BLACK)
            tft.text(vga1_bold_16x16, "aucune chance", largeur//2-len("aucune chance")//2*16, 20+64, st7789.WHITE, st7789.BLACK)
            tft.text(vga1_bold_16x16, "contre toi...", largeur//2-len("contre toi...")//2*16, 20+96, st7789.WHITE, st7789.BLACK)
        else:
            tft.text(vga1_bold_16x16, "Phew, c'est", largeur//2-len("Phew, c'est")//2*16, 20+32, st7789.WHITE, st7789.BLACK)
            tft.text(vga1_bold_16x16, "pas passe loin", largeur//2-len("pas passe loin")//2*16, 20+64, st7789.WHITE, st7789.BLACK)

oled_petit.fill(0)
oled_petit.text("PARTIE TERMINEE", 5, 0)
oled_petit.text(f"Score: {score_g}-{score_d}", 20, 17)

if heart_rate_list:
    BPM_mean = sum(heart_rate_list) / len(heart_rate_list)
    BPM_max = max(heart_rate_list)
    BPM_min = min(heart_rate_list)
else:
    BPM_mean = 0
    BPM_max = 0
    BPM_min = 0

oled_petit.text(f"BPM moyen: {int(BPM_mean)}", 10, 35)
oled_petit.text(f"BPM max: {BPM_max}", 10, 45)
oled_petit.text(f"BPM min: {BPM_min}", 10, 55)
oled_petit.show()


freq_valides = [f for f in sound_frequency_list if f > 50 and f < 2000]
if freq_valides:
    f_min = min(freq_valides)
    f_max = max(freq_valides)
    
    # fréquence de base déjà calibrée; on sépare grave/aigu autour de cette ref
    graves = [f for f in freq_valides if f < frequence_de_base]
    aigues = [f for f in freq_valides if f > frequence_de_base]

    if len(graves) > len(aigues):
        tendance1 = "Tu as fait plus"
        tendance2 = "de notes graves"
    elif len(aigues) > len(graves):
        tendance1 = "Tu as fait plus"
        tendance2 = "de notes aigues"
    else:
        tendance1 = "Autant de notes graves et aigues"

    note_min = freq_to_note(f_min)
    note_max = freq_to_note(f_max)


else:
    f_min = 0
    f_max = 0
    note_min = "Inconnue"
    note_max = "Inconnue"
    tendance1 = "Pas assez de son"

tft.text(vga1_bold_16x16, "STATS NOTES", 20, 170, st7789.WHITE, st7789.BLACK)
tft.text(vga2_8x8,"Plus grave: {}".format(note_min),10,200,st7789.WHITE,st7789.BLACK,)
tft.text(vga2_8x8,"Plus aigue: {}".format(note_max),10,230,st7789.WHITE,st7789.BLACK,)
tft.text(vga2_8x8,tendance1,10,260,st7789.WHITE,st7789.BLACK,)
tft.text(vga2_8x8,tendance2,10,290,st7789.WHITE,st7789.BLACK,)