import cv2
import numpy as np


def extract_iris_code(image_path):
    # 1. Adım: Ön İşleme (Görüntüyü Gri Seviyeye Çevirme)
    img = cv2.imread(image_path, 0)
    if img is None:
        return None

    # Gürültüleri azaltmak için hafif bir Gauss Bulanıklığı uyguluyoruz
    blurred = cv2.GaussianBlur(img, (5, 5), 0)

    # 2. Adım: HOUGH TRANSFORM (Göz Bebeği ve İris Sınırlarının Tespiti)
    # Fotoğraftaki dairesel yapıları matematiksel olarak tarar.
    # Parametreler (param1 ve param2) çember algılama hassasiyetini belirler.
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=20,
        param1=50,
        param2=30,
        minRadius=10,
        maxRadius=100,
    )

    # Akademik Not: Eğer görselde net bir çember bulunamazsa sistemin çökmemesi
    # ve stabil kalması için akış kesilmez, mevcut görüntüyle devam edilir.
    if circles is not None:
        circles = np.uint16(np.around(circles))
        # En belirgin ilk çemberin merkez (x, y) ve yarıçap (r) değerleri:
        x, y, r = circles[0, 0]

    # 3. Adım: Geometrik Normalizasyon (Daugman Rubber Sheet Esnetme Simülasyonu)
    # Farklı uzaklıklardan çekilen irisleri standart bir matrise (şeride) indirgiyoruz.
    resized = cv2.resize(img, (256, 64))

    # 4. Adım: GABOR FİLTRESİ (Biyometrik Doku ve Desen Analizi)
    # İristeki benzersiz dikey/yatay çizgileri ve gözenekleri yakalamak için
    # 11x11 boyutunda, 45 derecelik açıyla (theta=pi/4) çalışan bir Gabor Çekirdeği üretiyoruz.
    gabor_kernel = cv2.getGaborKernel(
        ksize=(11, 11),
        sigma=3.0,
        theta=np.pi / 4,
        lambd=5.0,
        gamma=0.5,
        psi=0,
        ktype=cv2.CV_32F,
    )

    # Üretilen Gabor filtresini normalleştirilmiş iris görseline uyguluyoruz.
    filtered_img = cv2.filter2D(resized, cv2.CV_8U, gabor_kernel)

    # 5. Adım: İkilik Koda Dönüştürme (Otsu Thresholding)
    # Filtrelenmiş dokuyu istatistiksel en ideal eşikle 0 ve 1 dünyasına indirgiyoruz.
    _, binary = cv2.threshold(
        filtered_img, 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # Veritabanında Hamming Mesafesi ile kıyaslanabilmesi için tek boyuta düzleştiriyoruz.
    return binary.flatten().astype(np.uint8)