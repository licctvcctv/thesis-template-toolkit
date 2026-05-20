package com.example.lebei;

import android.app.Application;
//import com.tencent.tcb.TCBCloud;
//import com.tencent.tcb.constants.CloudBaseConfig;

public class MyApplication extends Application {

    // 你的环境ID
    private static final String ENV_ID = "lebei-d2gfsxmle37c87eb";

    @Override
    public void onCreate() {
        super.onCreate();

        // 初始化 CloudBase（开发测试阶段仅使用环境ID，后续可补充安全凭证）
//        CloudBaseConfig config = new CloudBaseConfig.Builder()
//                .setEnvId(ENV_ID)
//                .build();
//        TCBCloud.getInstance(this).init(config);
    }
}