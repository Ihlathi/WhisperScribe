#include "WiFi.h"
#include "esp_camera.h"
#include <HTTPClient.h>

const char *ssid = "ssid";
const char *password = "password";

// define pins directly (ai thinker in this case)
#define PWDN_GPIO_NUM 32
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM 0
#define SIOD_GPIO_NUM 26
#define SIOC_GPIO_NUM 27
#define Y9_GPIO_NUM 35
#define Y8_GPIO_NUM 34
#define Y7_GPIO_NUM 39
#define Y6_GPIO_NUM 36
#define Y5_GPIO_NUM 21
#define Y4_GPIO_NUM 19
#define Y3_GPIO_NUM 18
#define Y2_GPIO_NUM 5
#define VSYNC_GPIO_NUM 25
#define HREF_GPIO_NUM 23
#define PCLK_GPIO_NUM 22
#define TORCH_LED_GPIO_NUM 4

// ===================
//  Arduino Functions
// ===================

void setup() {
    Serial.begin(115200); // for debug

    // setup functions
    connectWifi();
    initCamera();
}

void loop() {
    for (int i = 0; i < 3; i++) {
        bool doThing = takePhoto();
        if (doThing) {
            break;
        }
    }
    delay(15000);
}

// =================
//  Other Functions
// =================

// wifi yay
void connectWifi() {
    WiFi.begin(ssid, password);
    WiFi.setSleep(false);

    Serial.print("WiFi connecting");

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("");
        Serial.println("Failed, will try again on photo capture");
        return;
    }
    else {
        Serial.println("");
        Serial.println("WiFi connected");
    }
}

void initCamera() {
    // set config
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sscb_sda = SIOD_GPIO_NUM;
    config.pin_sscb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;


    if (psramFound()) {
    config.frame_size = FRAMESIZE_UXGA;
    config.jpeg_quality = 10;
    config.fb_count = 2;
    }
    else {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
    }

    // init camera with config
    esp_err_t err = esp_camera_init(&config);

    // if the camera decides to be funky
    if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    ESP.restart();
    }
}

// capture photo and hand off to send function
bool takePhoto() {
    // "auto" fix quality issues
    for (int i = 0; i < 3; i++) {
        camera_fb_t *fb = esp_camera_fb_get(); // get prep frame buffer

        if (!fb) {
            Serial.println("get prep frame buffer failed, retrying...");
            esp_camera_fb_return(fb); // release frame buffer
            return false;
        }
        else {
            Serial.printf("got prep frame buffer #%d/2\n", i + 1);
        }
        esp_camera_fb_return(fb); // release prep frame buffer
    }

    Serial.println("getting final frame buffer");
    camera_fb_t *fb = esp_camera_fb_get(); // get final frame buffer

    if (!fb) {
        Serial.println("get final frame buffer failed");
        esp_camera_fb_return(fb); // release frame buffer
        return false;
    }
    else {
        Serial.println("got final frame buffer");
    }

    for (int i = 0; i < 3; i++) {
        if (sendPhoto(fb->buf, fb->len)) {
            Serial.println("photo sent");
            esp_camera_fb_return(fb); // release frame buffer after success
            return true;
        } 
        else {
            Serial.printf("failed to send photo (try %d)", i + 1);
        }
    } 

    esp_camera_fb_return(fb); // release frame buffer after fail
    return false;
}

bool sendPhoto(uint8_t* buf, size_t len) {
        if (WiFi.status() != WL_CONNECTED) {
            connectWifi();
            if (WiFi.status() == WL_CONNECTED) {
                Serial.println("Wifi reconnected");
            }
            else {
                Serial.println("it keeps failing, get better wifi");
                return false;
            }
        }

        HTTPClient http; //init object

        http.begin("http://192.168.0.238:5002/upload");
        http.addHeader("Content-Type", "image/jpeg");

        int responseCode = http.POST(buf, len);

        if (responseCode > 0) {
            Serial.printf("Server response: %d\n", responseCode);
            http.end();
            return true;
        }
        else {
            String error = http.errorToString(responseCode);
            Serial.printf("POST failed: %s\n", error);
            http.end();
            return false;
        }
}