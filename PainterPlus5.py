
import speech_recognition as sr
import pyttsx3
import os
import io
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation

def speech_to_text():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio).lower()
        return text
    except sr.UnknownValueError:
        print("Sorry, I could not understand what you said.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None

def say_text(text):
    print(text)
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def save_and_exit(root, img_path):
    save_option = tk.messagebox.askquestion("Save Image", "Do you want to save the image?")
    
    if save_option == 'yes':
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            img = Image.open(img_path)
            img.save(file_path)
            say_text("Image saved successfully.")
        else:
            say_text("Image not saved.")

    root.destroy()  

def generate_image(prompt):
    stability_api = client.StabilityInference(
        key=os.environ['STABILITY_KEY'],
        verbose=True,
        engine="stable-diffusion-xl-1024-v1-0",
    )

    answers = stability_api.generate(
        prompt=prompt,
        seed=4253978046,
        steps=50,
        cfg_scale=8.0,
        width=1024,
        height=1024,
        samples=1,
        sampler=generation.SAMPLER_K_DPMPP_2M,
    )

    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                print("Your request activated the API's safety filters and could not be processed."
                      "Please modify the prompt and try again.")
            if artifact.type == generation.ARTIFACT_IMAGE:
                img_path = "temp_image.png"
                img = Image.open(io.BytesIO(artifact.binary))
                img.save(img_path)

                root = tk.Tk()
                root.attributes('-fullscreen', True)
                img = ImageTk.PhotoImage(file=img_path)
                panel = tk.Label(root, image=img)
                panel.pack(fill=tk.BOTH, expand=tk.YES)

                save_and_exit(root, img_path) 

                root.mainloop()

                return img_path

    return None

def main():
    os.environ['STABILITY_KEY'] = 'sk-qco3cKOtLCLDzLzutgswfD7ePY5ZyhyYybD8IH2DV9NVQjaI' 

    while True:
        while True:
            trigger_phrase = speech_to_text()
            if trigger_phrase == "hello painter":
                break

        say_text("Hello, what would you like me to paint?")
        
        user_prompt = speech_to_text()

        if user_prompt:
            say_text("Painting your masterpiece")
            generated_image_path = generate_image(user_prompt)

            if generated_image_path:
                print(f"Generated image saved at: {generated_image_path}")
                say_text("All done")
            else:
                say_text("Sorry, there was an error generating the image.")

if __name__ == "__main__":
    main()
