package com.example.myapplication;

import androidx.appcompat.app.AppCompatActivity;

import android.app.Activity;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Bundle;
import android.util.Log;
import android.widget.TextView;

public class MainActivity extends Activity implements SensorEventListener {

    private Sensor mAccel;
    private SensorManager mSensorManager;

    private float[] sensorValues = null;

    @Override
    protected void onCreate(Bundle    savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        mSensorManager = (SensorManager) getSystemService(SENSOR_SERVICE);
        mAccel = mSensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);

        if(mAccel == null)
        {
            finish();
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        // Register for sensor updates
        mSensorManager.registerListener(this, mAccel,SensorManager.SENSOR_DELAY_FASTEST);
    }

    @Override
    protected void onPause() {
        super.onPause();
        mSensorManager.unregisterListener(this);
    }

    @Override
    public void onSensorChanged(SensorEvent event) {
        if (event.sensor.getType() == Sensor.TYPE_ACCELEROMETER) {
            sensorValues = new float[3];
            System.arraycopy(event.values, 0, sensorValues, 0, 3);
        }

        if (sensorValues != null) {
            TextView textView = (TextView )findViewById(R.id.Magikarp);
            textView.setText(String.format("%f %f %f",sensorValues[0],sensorValues[1],sensorValues[2]));
            Log.d("abc", "gx : "+ sensorValues[0]+" gy : "+ sensorValues[1]+" gz : "+ sensorValues[2]);
        }
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {
        // N/A
    }
}

