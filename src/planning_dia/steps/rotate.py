import cv2
import numpy as np


def rotate(img: np.ndarray, debug_dir: str = None) -> np.ndarray:
    """
    Détecte si l'image est en portrait ou paysage et la remet droite.
    Pour un planning A4, on veut toujours paysage (width > height).
    """
    h, w = img.shape[:2]

    # Si l'image est en portrait → rotation 90° horaire
    if h > w:
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        h, w = img.shape[:2]

    # Correction d'inclinaison fine (deskew)
    img = _deskew(img)

    if debug_dir:
        cv2.imwrite(f"{debug_dir}/01_rotated.jpg", img)

    return img


def _deskew(img: np.ndarray) -> np.ndarray:
    """Corrige une légère inclinaison via détection de lignes."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)

    if lines is None:
        return img

    angles = []
    for x1, y1, x2, y2 in lines[:, 0]:
        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
        # On garde uniquement les lignes quasi-horizontales
        if -20 < angle < 20:
            angles.append(angle)

    if not angles:
        return img

    median_angle = np.median(angles)

    # Pas de correction si l'angle est négligeable
    if abs(median_angle) < 0.5:
        return img

    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), median_angle, 1.0)
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)