import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import time
import io


# PAGE CONFIG


st.set_page_config(
    page_title="Plant Disease Detection",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #f7faf7;
}

.block-container {
    max-width: 900px;
    padding-top: 2rem;
}

.hero {
    text-align: center;
    padding: 20px;
}

.hero h1 {
    font-size: 42px;
    margin-bottom: 5px;
}

.hero p {
    font-size: 18px;
    color: #666;
}

/* Falling leaves */

.leaf {
    position: fixed;
    top: -60px;
    font-size: 35px;
    animation: fall 4s linear infinite;
    z-index: 999;
}

.leaf1 {
    left: 10%;
    animation-delay: 0s;
}

.leaf2 {
    left: 30%;
    animation-delay: 1s;
}

.leaf3 {
    left: 55%;
    animation-delay: 2s;
}

.leaf4 {
    left: 75%;
    animation-delay: 0.5s;
}

.leaf5 {
    left: 90%;
    animation-delay: 1.5s;
}

@keyframes fall {

    0% {
        transform: translateY(-80px) rotate(0deg);
        opacity: 0;
    }

    15% {
        opacity: 1;
    }

    100% {
        transform: translateY(100vh) rotate(360deg);
        opacity: 0;
    }

}

/* Report Card */

.report-card {
    background: white;
    border-radius: 25px;
    padding: 30px;
    margin-top: 25px;
    box-shadow: 0 10px 35px rgba(0,0,0,0.12);
    border: 1px solid #e2e8e2;
}

.report-header {
    text-align: center;
    padding-bottom: 15px;
}

.report-header h2 {
    color: #245c36;
    margin-bottom: 4px;
}

.report-header p {
    color: #777;
}

.disease-title {
    text-align: center;
    font-size: 30px;
    font-weight: 700;
    color: #183b25;
    margin-top: 20px;
}

.confidence {
    text-align: center;
    font-size: 20px;
    font-weight: 600;
    margin: 10px;
}

.info-section {
    background: #f5f9f5;
    border-radius: 15px;
    padding: 18px;
    margin-top: 15px;
}

.info-section h4 {
    color: #245c36;
    margin-bottom: 7px;
}

.footer-note {
    text-align: center;
    color: #777;
    font-size: 12px;
    margin-top: 20px;
}

</style>
""", unsafe_allow_html=True)



# LOADING ANIMATION


if "loaded" not in st.session_state:

    st.markdown("""
    <div class="leaf leaf1">🍃</div>
    <div class="leaf leaf2">🌿</div>
    <div class="leaf leaf3">🍃</div>
    <div class="leaf leaf4">🌿</div>
    <div class="leaf leaf5">🍃</div>
    """, unsafe_allow_html=True)

    loading = st.empty()

    loading.markdown(
        "<h2 style='text-align:center;'>🌱 Preparing Plant Disease AI...</h2>",
        unsafe_allow_html=True
    )

    time.sleep(2)

    loading.empty()

    st.session_state.loaded = True



# HEADER


st.markdown("""
<div class="hero">

<h1>🌿 Plant Disease Detection</h1>

<p>
AI-powered plant leaf disease detection and health analysis
</p>

</div>
""", unsafe_allow_html=True)

st.divider()



# DISEASE DATABASE


disease_info = {

    "Apple___Apple_scab": {
        "name": "Apple — Apple Scab",
        "description": "A fungal disease that causes dark olive or brown lesions on apple leaves and fruit.",
        "treatment": "Remove infected leaves and fruit. Apply an appropriate fungicide according to local agricultural recommendations.",
        "prevention": "Keep the orchard clean, remove fallen leaves and maintain good air circulation."
    },

    "Apple___Black_rot": {
        "name": "Apple — Black Rot",
        "description": "A fungal disease that can cause leaf spots, fruit rot and branch damage.",
        "treatment": "Remove infected plant material and prune affected branches. Use a suitable fungicide when necessary.",
        "prevention": "Remove dead wood and fallen fruit and maintain good orchard sanitation."
    },

    "Apple___Cedar_apple_rust": {
        "name": "Apple — Cedar Apple Rust",
        "description": "A fungal disease producing yellow-orange spots on apple leaves.",
        "treatment": "Remove heavily infected leaves and use an appropriate fungicide if recommended.",
        "prevention": "Maintain good airflow and manage nearby alternate hosts such as cedar or juniper."
    },

    "Apple___healthy": {
        "name": "Apple — Healthy",
        "description": "The uploaded apple leaf appears healthy.",
        "treatment": "No disease treatment is required.",
        "prevention": "Continue regular watering, nutrition, pruning and monitoring."
    },

    "Blueberry___healthy": {
        "name": "Blueberry — Healthy",
        "description": "The uploaded blueberry leaf appears healthy.",
        "treatment": "No disease treatment is required.",
        "prevention": "Maintain proper soil moisture, nutrition and good air circulation."
    },

    "Cherry___Powdery_mildew": {
        "name": "Cherry — Powdery Mildew",
        "description": "A fungal disease producing white powder-like growth on leaves and shoots.",
        "treatment": "Remove severely affected parts and apply an appropriate fungicide if necessary.",
        "prevention": "Avoid excessive nitrogen and maintain good air circulation."
    },

    "Cherry___healthy": {
        "name": "Cherry — Healthy",
        "description": "The uploaded cherry leaf appears healthy.",
        "treatment": "No disease treatment is required.",
        "prevention": "Maintain proper watering, nutrition and regular monitoring."
    },

    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "name": "Corn — Cercospora Leaf Spot / Gray Leaf Spot",
        "description": "A fungal disease that creates gray or brown rectangular lesions on maize leaves.",
        "treatment": "Remove infected debris and consider an appropriate fungicide where recommended.",
        "prevention": "Use resistant varieties, rotate crops and maintain field sanitation."
    },

    "Corn_(maize)___Common_rust_": {
        "name": "Corn — Common Rust",
        "description": "A fungal disease producing reddish-brown rust pustules on maize leaves.",
        "treatment": "Monitor disease development and use an appropriate fungicide when economically justified.",
        "prevention": "Use resistant varieties and maintain proper crop management."
    },

    "Corn_(maize)___Northern_Leaf_Blight": {
        "name": "Corn — Northern Leaf Blight",
        "description": "A fungal disease causing long gray-green or brown lesions on maize leaves.",
        "treatment": "Remove infected crop debris and consider suitable fungicide management.",
        "prevention": "Use resistant hybrids and practice crop rotation."
    },

    "Corn_(maize)___healthy": {
        "name": "Corn — Healthy",
        "description": "The uploaded maize leaf appears healthy.",
        "treatment": "No disease treatment is required.",
        "prevention": "Maintain proper irrigation, nutrition and field monitoring."
    },

    "Grape___Black_rot": {
        "name": "Grape — Black Rot",
        "description": "A fungal disease that causes brown leaf spots and dark fruit lesions.",
        "treatment": "Remove infected leaves and fruit and use an appropriate fungicide if required.",
        "prevention": "Maintain vineyard sanitation and good air circulation."
    },

    "Grape___Esca_(Black_Measles)": {
        "name": "Grape — Esca / Black Measles",
        "description": "A complex grapevine disease that can cause leaf discoloration and fruit damage.",
        "treatment": "Remove severely affected plant material and consult a local plant disease specialist.",
        "prevention": "Use healthy planting material and minimize pruning wounds."
    },

    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "name": "Grape — Leaf Blight",
        "description": "A fungal leaf disease that produces dark spots and can reduce leaf health.",
        "treatment": "Remove infected material and apply suitable disease management when required.",
        "prevention": "Maintain good vineyard sanitation and airflow."
    },

    "Grape___healthy": {
        "name": "Grape — Healthy",
        "description": "The uploaded grape leaf appears healthy.",
        "treatment": "No disease treatment is required.",
        "prevention": "Continue proper irrigation, pruning and vineyard monitoring."
    },

    "Orange___Haunglongbing_(Citrus_greening)": {
        "name": "Orange — Huanglongbing / Citrus Greening",
        "description": "A serious citrus disease associated with leaf mottling, yellowing and reduced plant productivity.",
        "treatment": "There is no reliable cure for infected trees. Management focuses on controlling insect vectors and removing infected trees where recommended.",
        "prevention": "Use healthy nursery plants and manage citrus psyllid populations."
    },

    "Peach___Bacterial_spot": {
        "name": "Peach — Bacterial Spot",
        "description": "A bacterial disease that causes small dark spots on leaves and fruit.",
        "treatment": "Remove severely affected material and follow locally recommended bacterial disease management.",
        "prevention": "Maintain good orchard sanitation and avoid unnecessary leaf wetness."
    },

    "Peach___healthy": {
        "name": "Peach — Healthy",
        "description": "The uploaded peach leaf appears healthy.",
        "treatment": "No disease treatment is required.",
        "prevention": "Maintain proper irrigation, nutrition and orchard sanitation."
    },

    "Pepper,_bell___Bacterial_spot": {
        "name": "Bell Pepper — Bacterial Spot",
        "description": "A bacterial disease causing dark spots and lesions on pepper leaves and fruit.",
        "treatment": "Remove infected plant material and follow locally recommended bacterial disease control.",
        "prevention": "Use clean seeds, avoid overhead irrigation and maintain plant spacing."
    },

    "Pepper,_bell___healthy": {
        "name": "Bell Pepper — Healthy",
        "description": "The uploaded bell pepper leaf appears healthy.",
        "treatment": "No disease treatment is required.",
        "prevention": "Maintain proper watering, nutrition and regular inspection."
    },

    "Potato___Early_blight": {
        "name": "Potato — Early Blight",
        "description": "A fungal disease causing brown circular lesions, often with concentric rings.",
        "treatment": "Remove infected foliage and use an appropriate fungicide according to local recommendations.",
        "prevention": "Rotate crops, maintain plant nutrition and remove infected debris."
    },

    "Potato___Late_blight": {
        "name": "Potato — Late Blight",
        "description": "A destructive disease causing dark water-soaked lesions on potato leaves.",
        "treatment": "Remove infected plant material and use recommended fungicide management promptly.",
        "prevention": "Use healthy seed, avoid prolonged leaf wetness and monitor plants regularly."
    },

    "Potato___healthy": {
        "name": "Potato — Healthy",
        "description": "The uploaded potato leaf appears healthy.",
        "treatment": "No disease treatment is required.",
        "prevention": "Maintain good irrigation, nutrition and crop monitoring."
    },

    "Raspberry___healthy": {
        "name": "Raspberry — Healthy",
        "description": "The uploaded raspberry leaf appears healthy.",
        "treatment": "No disease treatment is required.",
        "prevention": "Maintain good airflow, watering and plant nutrition."
    },

    "Soybean___healthy": {
        "name": "Soybean — Healthy",
        "description": "The uploaded soybean leaf appears healthy.",
        "treatment": "No disease treatment is required.",
        "prevention": "Maintain balanced nutrition, irrigation and field monitoring."
    },

    "Squash___Powdery_mildew": {
        "name": "Squash — Powdery Mildew",
        "description": "A fungal disease that produces white powder-like patches on leaves.",
        "treatment": "Remove severely infected leaves and use an appropriate fungicide if necessary.",
        "prevention": "Improve airflow, avoid excessive nitrogen and monitor leaves regularly."
    },

    "Strawberry___Leaf_scorch": {
        "name": "Strawberry — Leaf Scorch",
        "description": "A fungal disease producing dark purple or brown spots that may cause leaf tissue to dry.",
        "treatment": "Remove infected leaves and improve plant management. Use appropriate fungicide when recommended.",
        "prevention": "Maintain good airflow, spacing and field sanitation."
    },

    "Strawberry___healthy": {
        "name": "Strawberry — Healthy",
        "description": "The uploaded strawberry leaf appears healthy.",
        "treatment": "No disease treatment is required.",
        "prevention": "Maintain adequate watering, nutrition and regular monitoring."
    },

    "Tomato___Bacterial_spot": {
        "name": "Tomato — Bacterial Spot",
        "description": "A bacterial disease that causes small dark spots on tomato leaves and fruit.",
        "treatment": "Remove infected material and follow locally recommended bacterial disease control.",
        "prevention": "Avoid overhead watering, use clean planting material and maintain good airflow."
    },

    "Tomato___Early_blight": {
        "name": "Tomato — Early Blight",
        "description": "A fungal disease producing brown spots with concentric rings on tomato leaves.",
        "treatment": "Remove infected leaves and use an appropriate fungicide when necessary.",
        "prevention": "Rotate crops, mulch around plants and avoid prolonged leaf wetness."
    },

    "Tomato___Late_blight": {
        "name": "Tomato — Late Blight",
        "description": "A serious disease that causes dark, water-soaked lesions on tomato leaves and can spread rapidly.",
        "treatment": "Remove infected plant material promptly and use an appropriate fungicide according to local agricultural guidance.",
        "prevention": "Avoid prolonged leaf wetness, provide good airflow and monitor plants frequently."
    },

    "Tomato___Leaf_Mold": {
        "name": "Tomato — Leaf Mold",
        "description": "A fungal disease commonly associated with humid conditions and yellow or brown leaf spots.",
        "treatment": "Remove infected leaves and improve ventilation. Use suitable fungicide management if necessary.",
        "prevention": "Reduce humidity, improve airflow and avoid excessive leaf wetness."
    },

    "Tomato___Septoria_leaf_spot": {
        "name": "Tomato — Septoria Leaf Spot",
        "description": "A fungal disease producing numerous small circular spots on tomato leaves.",
        "treatment": "Remove infected lower leaves and use suitable fungicide management when recommended.",
        "prevention": "Avoid overhead irrigation, mulch soil and remove infected plant debris."
    },

    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "name": "Tomato — Spider Mites",
        "description": "Tiny pests that feed on leaf tissue and may cause yellowing, stippling and leaf drying.",
        "treatment": "Wash foliage with water and use appropriate mite-control methods if infestation is severe.",
        "prevention": "Monitor leaves regularly and avoid excessive plant stress or dusty conditions."
    },

    "Tomato___Target_Spot": {
        "name": "Tomato — Target Spot",
        "description": "A fungal disease causing circular brown lesions that may develop concentric rings.",
        "treatment": "Remove infected foliage and apply suitable fungicide management when recommended.",
        "prevention": "Improve airflow, avoid overhead irrigation and remove infected debris."
    },

    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "name": "Tomato — Yellow Leaf Curl Virus",
        "description": "A viral disease that causes leaf curling, yellowing and reduced plant growth.",
        "treatment": "There is no direct cure for viral infection. Remove severely infected plants and manage whitefly populations.",
        "prevention": "Use healthy seedlings, control whiteflies and remove infected plants."
    },

    "Tomato___Tomato_mosaic_virus": {
        "name": "Tomato — Mosaic Virus",
        "description": "A viral disease that can cause mosaic patterns, leaf distortion and reduced plant growth.",
        "treatment": "There is no direct cure. Remove infected plants and sanitize tools.",
        "prevention": "Use healthy planting material, disinfect tools and avoid handling plants unnecessarily."
    },

    "Tomato___healthy": {
        "name": "Tomato — Healthy",
        "description": "The uploaded tomato leaf appears healthy.",
        "treatment": "No disease treatment is required.",
        "prevention": "Continue regular watering, balanced nutrition and plant monitoring."
    }
}



# LOAD MODEL


@st.cache_resource
def load_model():

    return tf.keras.models.load_model(
        "plant_disease_model.keras",
        compile=False
    )



# IMAGE UPLOAD


st.subheader("📷 Upload Plant Leaf")

uploaded_file = st.file_uploader(
    "Upload any JPG, JPEG or PNG image",
    type=["jpg", "jpeg", "png"],
    help="Image can be any resolution or size."
)



# PREDICTION


if uploaded_file is not None:

    image = Image.open(uploaded_file).convert("RGB")

    st.image(
        image,
        caption="Uploaded Leaf Image",
        use_container_width=True
    )

    st.write("")

    if st.button(
        "🔍 Detect Disease",
        use_container_width=True
    ):

        with st.spinner("🤖 AI is analyzing the leaf..."):

            model = load_model()

            # Model input = 128 x 128
            resized_image = image.resize(
                (128, 128),
                Image.Resampling.LANCZOS
            )

            img_array = np.array(
                resized_image,
                dtype=np.float32
            )

            img_array = np.expand_dims(
                img_array,
                axis=0
            )

            img_array = img_array / 255.0

            prediction = model.predict(
                img_array,
                verbose=0
            )

            predicted_class = int(
                np.argmax(prediction[0])
            )

            confidence = float(
                np.max(prediction[0]) * 100
            )


        # CLASS MAPPING


        class_names = list(disease_info.keys())

        predicted_label = class_names[predicted_class]

        info = disease_info[predicted_label]



        # STATUS


        if "Healthy" in info["name"]:

            status = "🟢 HEALTHY"

        else:

            status = "🔴 DISEASE DETECTED"



        # SINGLE REPORT CARD

        st.markdown(
            '<div class="report-card">',
            unsafe_allow_html=True
        )

        st.markdown("""
        <div class="report-header">

        <h2>🌿 PLANT HEALTH REPORT</h2>

        <p>AI-powered disease analysis</p>

        </div>
        """, unsafe_allow_html=True)




        st.image(
            image,
            use_container_width=True
        )


        # STATUS

        st.markdown(
            f"""
            <div style="
                text-align:center;
                font-size:18px;
                font-weight:700;
                margin-top:15px;
            ">
            {status}
            </div>
            """,
            unsafe_allow_html=True
        )


        # DISEASE NAME

        st.markdown(
            f"""
            <div class="disease-title">
            {info["name"]}
            </div>
            """,
            unsafe_allow_html=True
        )


        # CONFIDENCE

        st.markdown(
            f"""
            <div class="confidence">
            🎯 Confidence: {confidence:.2f}%
            </div>
            """,
            unsafe_allow_html=True
        )

        st.progress(
            min(int(confidence), 100)
        )


        # CONFIDENCE MESSAGE

        if confidence >= 70:

            st.success(
                "🟢 High confidence prediction"
            )

        elif confidence >= 50:

            st.warning(
                "🟡 Moderate confidence — "
                "use a clearer leaf image for better reliability."
            )

        else:

            st.error(
                "🔴 Low confidence — "
                "please upload a clearer leaf image."
            )


        # ABOUT

        st.markdown(
            f"""
            <div class="info-section">

            <h4>📋 About the Detection</h4>

            <p>{info["description"]}</p>

            </div>
            """,
            unsafe_allow_html=True
        )


        # TREATMENT

        st.markdown(
            f"""
            <div class="info-section">

            <h4>💊 Recommended Treatment</h4>

            <p>{info["treatment"]}</p>

            </div>
            """,
            unsafe_allow_html=True
        )


        # PREVENTION

        st.markdown(
            f"""
            <div class="info-section">

            <h4>🛡️ Prevention</h4>

            <p>{info["prevention"]}</p>

            </div>
            """,
            unsafe_allow_html=True
        )


        # DISCLAIMER

        st.markdown(
            """
            <div class="footer-note">

            ⚠️ AI-generated prediction.  
            For serious crop disease, consult a qualified
            agricultural expert.

            <br><br>

            🌿 Plant Disease Detection • Powered by TensorFlow

            </div>
            """,
            unsafe_allow_html=True
        )


        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )



        # DOWNLOADABLE REPORT CARD


        st.subheader("📥 Download Report Card")

        try:

            # Create report image
            card_width = 1000
            card_height = 1450

            report = Image.new(
                "RGB",
                (card_width, card_height),
                "white"
            )

            draw = ImageDraw.Draw(report)

            # Fonts
            try:

                title_font = ImageFont.truetype(
                    "arial.ttf",
                    42
                )

                subtitle_font = ImageFont.truetype(
                    "arial.ttf",
                    28
                )

                heading_font = ImageFont.truetype(
                    "arial.ttf",
                    30
                )

                normal_font = ImageFont.truetype(
                    "arial.ttf",
                    22
                )

            except:

                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
                heading_font = ImageFont.load_default()
                normal_font = ImageFont.load_default()


            # Header

            draw.text(
                (500, 45),
                "PLANT HEALTH REPORT",
                fill="#245c36",
                font=title_font,
                anchor="mm"
            )

            draw.text(
                (500, 90),
                "AI-Powered Plant Disease Detection",
                fill="#777777",
                font=normal_font,
                anchor="mm"
            )


            # Resize uploaded image

            preview = image.copy()

            preview.thumbnail(
                (700, 450)
            )

            image_x = (card_width - preview.width) // 2

            report.paste(
                preview,
                (image_x, 130)
            )


            # Disease

            y = 620

            draw.text(
                (500, y),
                info["name"],
                fill="#183b25",
                font=subtitle_font,
                anchor="mm"
            )

            y += 60

            draw.text(
                (500, y),
                f"Confidence: {confidence:.2f}%",
                fill="#333333",
                font=heading_font,
                anchor="mm"
            )


            # Status

            y += 55

            draw.text(
                (500, y),
                status.replace("🟢 ", "").replace("🔴 ", ""),
                fill="#245c36" if "Healthy" in info["name"] else "#b02a37",
                font=heading_font,
                anchor="mm"
            )


            # Divider

            y += 50

            draw.line(
                (80, y, 920, y),
                fill="#dddddd",
                width=3
            )


            # Text wrapping helper

            def draw_wrapped_text(
                text,
                x,
                y,
                width,
                font,
                fill="#333333"
            ):

                words = text.split()

                lines = []

                current = ""

                for word in words:

                    test = current + " " + word

                    bbox = draw.textbbox(
                        (0, 0),
                        test,
                        font=font
                    )

                    if bbox[2] - bbox[0] <= width:

                        current = test.strip()

                    else:

                        if current:
                            lines.append(current)

                        current = word

                if current:
                    lines.append(current)

                for line in lines:

                    draw.text(
                        (x, y),
                        line,
                        fill=fill,
                        font=font
                    )

                    y += 32

                return y


            # ABOUT

            y += 35

            draw.text(
                (80, y),
                "ABOUT",
                fill="#245c36",
                font=heading_font
            )

            y += 45

            y = draw_wrapped_text(
                info["description"],
                80,
                y,
                840,
                normal_font
            )


            # TREATMENT

            y += 30

            draw.text(
                (80, y),
                "RECOMMENDED TREATMENT",
                fill="#245c36",
                font=heading_font
            )

            y += 45

            y = draw_wrapped_text(
                info["treatment"],
                80,
                y,
                840,
                normal_font
            )


            # PREVENTION

            y += 30

            draw.text(
                (80, y),
                "PREVENTION",
                fill="#245c36",
                font=heading_font
            )

            y += 45

            y = draw_wrapped_text(
                info["prevention"],
                80,
                y,
                840,
                normal_font
            )


            # Footer

            draw.text(
                (500, 1400),
                "Plant Disease Detection • Powered by TensorFlow",
                fill="#777777",
                font=normal_font,
                anchor="mm"
            )

            draw.text(
                (500, 1430),
                "AI-generated prediction — consult an agricultural expert when needed.",
                fill="#999999",
                font=normal_font,
                anchor="mm"
            )




            img_buffer = io.BytesIO()

            report.save(
                img_buffer,
                format="PNG"
            )

            img_buffer.seek(0)


            st.download_button(
                label="⬇️ Download Report Card (PNG)",
                data=img_buffer,
                file_name="plant_disease_report.png",
                mime="image/png",
                use_container_width=True
            )

        except Exception as e:

            st.warning(
                "Report image could not be generated. "
                "The prediction result is still available above."
            )

            st.caption(
                f"Report generation details: {e}"
            )



# FOOTER file

st.divider()

st.caption(
    "🌿 Plant Disease Detection • Powered by TensorFlow"
)