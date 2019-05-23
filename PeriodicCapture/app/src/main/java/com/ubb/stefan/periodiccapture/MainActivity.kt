package com.ubb.stefan.periodiccapture

import android.Manifest
import android.app.Activity
import android.content.pm.PackageManager
import android.media.ImageReader
import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import java.util.*
import android.support.annotation.NonNull
import java.sql.Types.TIMESTAMP
import android.media.ImageReader.OnImageAvailableListener
import android.os.Handler
import android.os.HandlerThread
import android.util.Log
import kotlinx.android.synthetic.main.activity_main.*
import android.R.attr.port
import java.io.DataOutputStream
import java.io.FileInputStream
import java.net.Socket
import android.hardware.Camera.Parameters.FOCUS_MODE_CONTINUOUS_PICTURE
import android.support.v7.widget.DefaultItemAnimator
import android.support.v7.widget.LinearLayoutManager
import com.google.android.things.pio.Gpio
import com.google.android.things.pio.PeripheralManager
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.firestore.FirebaseFirestore
import com.google.firebase.firestore.ListenerRegistration
import com.google.firebase.firestore.EventListener
import com.ubb.stefan.periodiccapture.model.PlateEntry


class MainActivity : Activity() {
    private val mCamera: CameraHandler = CameraHandler.instance
    private var firestoreDB: FirebaseFirestore? = null
    private var firestoreListener: ListenerRegistration? = null
    private var mAuth: FirebaseAuth? = null
    private var user:String?=null
    private var plateEntries = mutableListOf<PlateEntry>()
    private lateinit var ledGpio: Gpio

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val pioService = PeripheralManager.getInstance()
        ledGpio = pioService.openGpio("BCM6")
        ledGpio.setDirection(Gpio.DIRECTION_OUT_INITIALLY_LOW)

        Log.d("Main:", "Main Activity created.")

        // We need permission to access the camera
        if (checkSelfPermission(Manifest.permission.CAMERA)
            != PackageManager.PERMISSION_GRANTED) {
            // A problem occurred auto-granting the permission
            Log.e("Main", "No permission")
            return
        }

        // Creates new handlers and associated threads for camera
        val mCameraThread = HandlerThread("CameraBackground")
        mCameraThread.start()
        val mCameraHandler =  Handler(mCameraThread.looper)

        mCamera.initializeCamera(this, mCameraHandler, mOnImageAvailableListener)

        btn_picture.setOnClickListener{
            takePicture()
        }


        // Init
        val handler = Handler()
        val runnable = object : Runnable {
            override fun run() {
                takePicture()
                handler.postDelayed(this, 1000)
            }
        }

        //Start
        handler.postDelayed(runnable, 1000)

        firestoreDB = FirebaseFirestore.getInstance()
        this.user = "1johKUqM3WMSUMHqBz9YyPrO3x63"

        loadPlateHistory(this.user!!)

        firestoreListener = firestoreDB!!.collection("parkinghistory")
            .whereEqualTo("user",this.user)
            .addSnapshotListener(EventListener { documentSnapshots, e ->
                if (e != null) {
                    Log.e("Stefan", "Listen failed!", e)
                    return@EventListener
                }
                val newPlateEntries = mutableListOf<PlateEntry>()

                if (documentSnapshots != null) {
                    for (doc in documentSnapshots) {
                        val plateEntry = doc.toObject(PlateEntry::class.java)
                        plateEntry.id = doc.id
                        newPlateEntries.add(plateEntry)
                    }
                }

                Log.d("Stefan","size of the new list:"+newPlateEntries.size.toString())
                Log.d("Stefan","size of the old list:"+plateEntries.size.toString())
                if(newPlateEntries.size > plateEntries.size) {
                    Log.d("Stefan","items were added should add")
                    var lastDate: Date? = null
                    if (this.plateEntries.size > 0) {
                        lastDate = this.plateEntries[0].time!!
                        for (plate in this.plateEntries) {
                            if (plate.time!! > lastDate)
                                lastDate = plate.time!!
                        }
                    }

                    var lastDateNewList: Date? = null
                    if (newPlateEntries.size > 0) {
                        lastDateNewList = newPlateEntries[0].time!!
                        for (plate in newPlateEntries) {
                            if (plate.time!! > lastDateNewList)
                                lastDateNewList = plate.time!!
                        }
                    }
                    if (lastDate != null && lastDateNewList != null && lastDate < lastDateNewList) {
                        Log.d("Stefan", "light the LED/elctro signal for garage opener")
                        ledGpio.value = true;
                        Thread.sleep(2000)
                    }
                }
                //update the list with the new one
                this.plateEntries = newPlateEntries
            })
    }
    private fun loadPlateHistory(uid:String) {
        firestoreDB!!.collection("parkinghistory")
            .whereEqualTo("user",uid)
            .get()
            .addOnCompleteListener { task ->
                if (task.isSuccessful) {
                    val platesList = mutableListOf<PlateEntry>()

                    for (doc in task.result!!) {
                        val plateEntry = doc.toObject<PlateEntry>(PlateEntry::class.java)
                        plateEntry.id = doc.id
                        platesList.add(plateEntry)
                    }
                    this.plateEntries = platesList

                } else {
                    Log.d("Stefan", "Error getting documents: ", task.exception)
                }
            }
    }
    private fun takePicture() {
        mCamera.takePicture()
        //set camera to continually auto-focus
    }

    /**
     * Listener for new camera images.
     */
    private val mOnImageAvailableListener = OnImageAvailableListener { reader ->
        val image = reader.acquireLatestImage()
        // get image bytes
        val imageBuf = image.planes[0].buffer
        val imageBytes = ByteArray(imageBuf.remaining())
        imageBuf.get(imageBytes)
        image.close()

        onPictureTaken(imageBytes)
    }

    /**
     * Upload image data to server to be processed.
     */
    private fun onPictureTaken(imageBytes: ByteArray?) {
        if (imageBytes != null) {
            Log.i("sending", "send image bytes on socket")

            val socket = Socket("192.168.43.115",12345)
            val dOut = DataOutputStream(socket.getOutputStream())
            dOut.write(imageBytes)
        }
    }
    override fun onStop() {
        ledGpio.close()

        super.onStop()
    }
}
