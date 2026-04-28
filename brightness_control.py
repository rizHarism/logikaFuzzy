import cv2
import mediapipe as mp
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import screen_brightness_control as sbc
import time

# ===== 1. SETUP FUZZY TRAPESIUM =====
# Input: Jumlah jari yang terbuka (0 sampai 5)
jumlah_jari = ctrl.Antecedent(np.arange(0, 6, 1), 'jumlah_jari')
# Output: Target Brightness (0-100%)
target_bright = ctrl.Consequent(np.arange(0, 101, 1), 'target_bright')

##Pakai Segitiga (trimf) agar setiap kenaikan angka jari langsung merubah nilai
jumlah_jari['nol'] = fuzz.trimf(jumlah_jari.universe, [0, 0, 1])
jumlah_jari['satu'] = fuzz.trimf(jumlah_jari.universe, [0, 1, 2])
jumlah_jari['dua'] = fuzz.trimf(jumlah_jari.universe, [1, 2, 3])
jumlah_jari['tiga'] = fuzz.trimf(jumlah_jari.universe, [2, 3, 4])
jumlah_jari['empat'] = fuzz.trimf(jumlah_jari.universe, [3, 4, 5])
jumlah_jari['lima'] = fuzz.trimf(jumlah_jari.universe, [4, 5, 5])

# Output dibagi rata per 20%
target_bright['0'] = fuzz.trimf(target_bright.universe, [0, 0, 20])
target_bright['20'] = fuzz.trimf(target_bright.universe, [0, 20, 40])
target_bright['40'] = fuzz.trimf(target_bright.universe, [20, 40, 60])
target_bright['60'] = fuzz.trimf(target_bright.universe, [40, 60, 80])
target_bright['80'] = fuzz.trimf(target_bright.universe, [60, 80, 100])
target_bright['100'] = fuzz.trimf(target_bright.universe, [80, 100, 100])

# Rules spesifik
rules = [
    ctrl.Rule(jumlah_jari['nol'], target_bright['0']),
    ctrl.Rule(jumlah_jari['satu'], target_bright['20']),
    ctrl.Rule(jumlah_jari['dua'], target_bright['40']),
    ctrl.Rule(jumlah_jari['tiga'], target_bright['60']),
    ctrl.Rule(jumlah_jari['empat'], target_bright['80']),
    ctrl.Rule(jumlah_jari['lima'], target_bright['100'])
]

bright_ctrl = ctrl.ControlSystem(rules)
bright_sim = ctrl.ControlSystemSimulation(bright_ctrl)
target_bright.defuzzify_method = 'mom'

# ===== 2. SETUP MEDIAPIPE =====
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
current_brightness = sbc.get_brightness()[0]

print("Sistem Aktif. Kepalkan tangan = 0%, Buka jari = +20% per jari.")

while True:
    success, img = cap.read()
    if not success: break
    img = cv2.flip(img, 1)
    results = hands.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    total_jari = 0

    if results.multi_hand_landmarks:
        for idx, hand_handedness in enumerate(results.multi_handedness):
            label = hand_handedness.classification[0].label # 'Left' atau 'Right'
            hand_lms = results.multi_hand_landmarks[idx]
            lm = hand_lms.landmark

            opened_fingers = []
            
            # 1. Logika 4 Jari (Telunjuk - Kelingking) -> Sama untuk kedua tangan
            tips = [8, 12, 16, 20]
            pips = [6, 10, 14, 18]
            for t, p in zip(tips, pips):
                if lm[t].y < lm[p].y:
                    opened_fingers.append(1)

            # 2. Logika Jempol (Harus beda antara Kiri dan Kanan)
            # Gunakan perbandingan sumbu X antara Ujung (4) dan Pangkal (3/2)
            if label == 'Right': # Tangan Kanan
                if lm[4].x < lm[3].x: opened_fingers.append(1)
            else: # Tangan Kiri
                if lm[4].x > lm[3].x: opened_fingers.append(1)

            total_jari = sum(opened_fingers)

            # Jalankan Fuzzy
            bright_sim.input['jumlah_jari'] = total_jari
            bright_sim.compute()
            hasil_fuzzy = bright_sim.output['target_bright']

            if total_jari == 5:
                hasil_fuzzy = 100.0
            elif total_jari == 0:
                hasil_fuzzy = 0.0

            # Logika Kenaikan per 5% (Smoothing)
            # Jika selisih hasil fuzzy dan brightness sekarang cukup besar
            if abs(hasil_fuzzy - current_brightness) >= 5:
                if hasil_fuzzy > current_brightness:
                    current_brightness += 5 # Naik per 5%
                else:
                    current_brightness -= 5 # Turun per 5%
                
                # Batasi 0-100 dan eksekusi
                current_brightness = np.clip(current_brightness, 0, 100)
                try:
                    sbc.set_brightness(int(current_brightness))
                except: pass

            mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)

    # Tampilan UI
    cv2.rectangle(img, (10, 10), (250, 120), (0,0,0), -1)
    cv2.putText(img, f"Jari: {total_jari}", (20, 50), 1, 2, (0, 255, 0), 2)
    cv2.putText(img, f"Layar: {current_brightness}%", (20, 100), 1, 2, (0, 255, 255), 2)

    cv2.imshow("UAS Finger Gesture Fuzzy", img)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()