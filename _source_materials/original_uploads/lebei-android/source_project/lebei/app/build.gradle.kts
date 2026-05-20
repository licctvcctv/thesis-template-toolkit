plugins {
    id("com.android.application")
    kotlin("android")
}

android {
    namespace = "com.example.lebei"
    compileSdk = 33

    defaultConfig {
        applicationId = "com.example.lebei"
        minSdk = 26
        targetSdk = 33
        versionCode = 1
        versionName = "1.0"
        // 模拟器访问本机 Spring Boot：http://10.0.2.2:8080 ；真机请改为电脑局域网 IP
        buildConfigField("String", "API_BASE_URL", "\"http://10.0.2.2:8080\"")
    }

    buildFeatures {
        viewBinding = true
        buildConfig = true
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }
}

dependencies {
    testImplementation("junit:junit:4.13.2")

    // 基础依赖
    implementation("androidx.core:core-ktx:1.9.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.9.0")

    // 导航组件（解决之前 navGraph 错误）
    implementation("androidx.navigation:navigation-fragment-ktx:2.5.3")
    implementation("androidx.navigation:navigation-ui-ktx:2.5.3")
    implementation("androidx.recyclerview:recyclerview:1.3.0")

    // Room：仅本地单词学习数据
    implementation("androidx.room:room-runtime:2.5.0")
    annotationProcessor("androidx.room:room-compiler:2.5.0")

    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("com.google.code.gson:gson:2.10.1")
}
