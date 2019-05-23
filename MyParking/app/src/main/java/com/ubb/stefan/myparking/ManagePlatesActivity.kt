package com.ubb.stefan.myparking

import android.content.Context
import android.os.Bundle
import android.support.design.widget.Snackbar
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.DefaultItemAnimator
import android.support.v7.widget.LinearLayoutManager
import android.util.Log
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.firestore.EventListener
import com.google.firebase.firestore.FirebaseFirestore
import com.google.firebase.firestore.ListenerRegistration
import com.ubb.stefan.myparking.adapter.PlateHistoryRecyclerViewAdapter
import com.ubb.stefan.myparking.adapter.PlateRecyclerViewAdapter
import com.ubb.stefan.myparking.model.PlateEntry
import kotlinx.android.synthetic.main.activity_main.*
import kotlinx.android.synthetic.main.activity_manage_plates.*
import kotlinx.android.synthetic.main.content_manage_plates.*
import android.content.DialogInterface
import android.support.v7.app.AlertDialog
import android.widget.EditText



class ManagePlatesActivity : AppCompatActivity() {

    private val TAG = "MangePlatesActivity"
    private var mAdapter: PlateRecyclerViewAdapter? = null
    private var firestoreDB: FirebaseFirestore? = null
    private var firestoreListener: ListenerRegistration? = null
    private var mAuth: FirebaseAuth? = null
    private var user:String?=null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_manage_plates)

        addPlateButton.setOnClickListener { view ->
            showAddItemDialog(this)
        }
        firestoreDB = FirebaseFirestore.getInstance()
        this.user =  intent.getStringExtra("uid")

        loadPlateHistory(this.user!!)
        firestoreListener = firestoreDB!!.collection("plates")
            .addSnapshotListener(EventListener { documentSnapshots, e ->
                if (e != null) {
                    Log.e(TAG, "Listen failed!", e)
                    return@EventListener
                }

                val plateEntries = mutableListOf<PlateEntry>()

                if (documentSnapshots != null) {
                    for (doc in documentSnapshots) {
                        val plateEntry = doc.toObject(PlateEntry::class.java)
                        plateEntry.id = doc.id
                        plateEntries.add(plateEntry)
                    }
                }

                mAdapter = PlateRecyclerViewAdapter(plateEntries, applicationContext, firestoreDB!!)
                rvPlatesList.adapter = mAdapter
            })


        mAuth = FirebaseAuth.getInstance()
        val user = mAuth!!.getCurrentUser()

    }

    private fun loadPlateHistory(uid:String) {
        firestoreDB!!.collection("plates")
            .whereEqualTo("user",uid)
            .get()
            .addOnCompleteListener { task ->
                if (task.isSuccessful) {
                    val productsList = mutableListOf<PlateEntry>()

                    for (doc in task.result!!) {
                        val plateEntry = doc.toObject<PlateEntry>(PlateEntry::class.java)
                        plateEntry.id = doc.id
                        productsList.add(plateEntry)
                    }

                    mAdapter = PlateRecyclerViewAdapter(productsList, applicationContext, firestoreDB!!)
                    val mLayoutManager = LinearLayoutManager(applicationContext)

                    rvPlatesList.layoutManager = mLayoutManager
                    rvPlatesList.itemAnimator = DefaultItemAnimator()
                    rvPlatesList.adapter = mAdapter
                } else {
                    Log.d(TAG, "Error getting documents: ", task.exception)
                }
            }
    }

    private fun showAddItemDialog(c: Context) {
        val data = HashMap<String, String>()
        data["user"] = this.user!!

        val newPlateRef = firestoreDB!!.collection("plates").document()


        val taskEditText = EditText(c)
        val dialog = AlertDialog.Builder(c)
            .setTitle("Add a new licence plate")
            .setMessage("What licence plate would you like to add?")
            .setView(taskEditText)
            .setPositiveButton("Add"
            ) { dialog, which -> val task = taskEditText.text.toString()
                data["plate"] = task
                newPlateRef.set(data)
                }
            .setNegativeButton("Cancel", null)
            .create()
        dialog.show()
    }

}
