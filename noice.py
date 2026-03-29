import noisereduce as nr
import librosa
import soundfile as sf
from scipy.signal import butter, lfilter
import os

def low_pass_filter(data, cutoff, sr): 
                    #ses sinyali, kesilecek min frekans, örnekleme frekansı


    nyquist = 0.5 * sr # Nyquist frekansı, örnekleme frekansının yarısıdır
    
    if cutoff >= nyquist:
        cutoff = nyquist - 100 # Güvenlik için kesme frekansını Nyquist'in biraz altına ayarlıyoruz
    normal_cutoff = cutoff / nyquist # Normalleştirilmiş kesme frekansı
    b, a = butter(5, normal_cutoff, btype='low') # Butterworth düşük geçiren filtre katsayıları
    return lfilter(b, a, data)

def clean_audio(input_path, output_path):
    """
    Ses dosyasını temizler:
    1. OGG dosyasını direkt oku 
    2. Low-pass filter
    3. Noise reduction
    4. WAV olarak kaydet
    """
    # librosa OGG'u direkt okur
    y, sr = librosa.load(input_path, sr=None, mono=True)

    # düşük geçiren filtre uygula
    y_filtered = low_pass_filter(y, cutoff=3000, sr=sr)

    # gürültü azaltma uygula
    reduced_noise = nr.reduce_noise(y=y_filtered, sr=sr)

    # temizlenmiş dosyayı WAV olarak kaydet
    sf.write(output_path, reduced_noise, sr)