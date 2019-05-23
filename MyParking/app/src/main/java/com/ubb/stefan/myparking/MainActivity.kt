package com.ubb.stefan.myparking

import android.app.Notification
import android.app.Notification.VISIBILITY_PUBLIC
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.media.RingtoneManager
import android.os.Build
import android.os.Bundle
import android.support.design.widget.NavigationView
import android.support.v4.app.NotificationCompat
import android.support.v4.app.NotificationManagerCompat
import android.support.v4.view.GravityCompat
import android.support.v7.app.ActionBarDrawerToggle
import android.support.v7.app.AppCompatActivity
import android.support.v7.widget.DefaultItemAnimator
import android.support.v7.widget.LinearLayoutManager
import android.util.Log
import android.view.Menu
import android.view.MenuItem
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.firestore.EventListener
import com.google.firebase.firestore.FirebaseFirestore
import com.google.firebase.firestore.ListenerRegistration
import com.ubb.stefan.myparking.adapter.PlateHistoryRecyclerViewAdapter
import com.ubb.stefan.myparking.model.PlateEntry
import kotlinx.android.synthetic.main.activity_main.*
import kotlinx.android.synthetic.main.app_bar_main.*
import kotlinx.android.synthetic.main.content_main.*
import android.widget.CompoundButton
import io.fabric.sdk.android.services.settings.IconRequest.build





class MainActivity : AppCompatActivity(), NavigationView.OnNavigationItemSelectedListener {

    private val TAG = "MainActivity"
    private var mAdapter: PlateHistoryRecyclerViewAdapter? = null
    private var firestoreDB: FirebaseFirestore? = null
    private var firestoreListener: ListenerRegistration? = null
    private var mAuth: FirebaseAuth? = null
    private var user:String?=null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        setSupportActionBar(toolbar)

        firestoreDB = FirebaseFirestore.getInstance()
        this.user =  intent.getStringExtra("uid")

        loadPlateHistory(this.user!!)

        firestoreListener = firestoreDB!!.collection("parkinghistory")
            .whereEqualTo("user",this.user)
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
                plateEntries.sort()

                if(mAdapter != null) {
                    mAdapter!!.getPlates()
                    mAdapter!!.getPlates().addAll(plateEntries)
                    val sum: MutableList<PlateEntry> = mAdapter!!.getPlates()

                    val diff:List<PlateEntry> = sum.groupBy { it.id }
                        .filter { it.value.size == 1 }
                        .flatMap { it.value }
                    Log.d("Stefan",diff[0].toString())
                    showNotification("Garage was accessed!","Licence Plate: " + diff[0].plate.toString())
                }

                mAdapter = PlateHistoryRecyclerViewAdapter(plateEntries, applicationContext, firestoreDB!!)
                mAdapter!!.sortList()
                rvPlateHistoryList.adapter = mAdapter


            })

        val toggle = ActionBarDrawerToggle(
            this, drawer_layout, toolbar, R.string.navigation_drawer_open, R.string.navigation_drawer_close
        )
        drawer_layout.addDrawerListener(toggle)
        toggle.syncState()

        mAuth = FirebaseAuth.getInstance()
        val user = mAuth!!.getCurrentUser()

        nav_view.setNavigationItemSelectedListener(this)

        newest.setOnCheckedChangeListener { buttonView, isChecked ->
            mAdapter!!.reverseList()
        }

    }

    private fun showNotification(title: String?, body: String?) {
        val open_activity_intent = Intent(this, MainActivity::class.java)
        val pending_intent = PendingIntent
            .getActivity(this, 0, open_activity_intent, PendingIntent.FLAG_CANCEL_CURRENT)

        val notification_manager:NotificationManager =
            this.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        val chanel_id = "3000";
        val name:CharSequence = "Channel Name";
        val description:String = "Chanel Description";
        val importance: Int = NotificationManager.IMPORTANCE_HIGH;
        val mChannel: NotificationChannel = NotificationChannel(chanel_id, name, importance);
        mChannel.description = description
        mChannel.enableLights(true)
        mChannel.lightColor = Color.BLUE
        notification_manager.createNotificationChannel(mChannel)
        val notification_builder = NotificationCompat.Builder(this, chanel_id)
        val soundUri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION)

        notification_builder.apply {
            setSmallIcon(R.drawable.ic_car)
            setContentTitle(title)
            setContentText(body)
            setAutoCancel(true)
            setSound(soundUri)
            setVibrate(longArrayOf(1000, 500, 1000))
            setStyle(NotificationCompat.BigTextStyle()
                    .bigText("Is this a mistake? If it is your garage might be in danger! Click here to se more details."))
            setVisibility(VISIBILITY_PUBLIC)
            setSound(soundUri)
            setChannelId(chanel_id)
            setContentIntent(pending_intent)
        }


        Log.d("Stefan","Showing the notification!")
        with(NotificationManagerCompat.from(this)) {
            // notificationId is a unique int for each notification that you must define
            notify(0, notification_builder.build())
        }

    }

    private fun loadPlateHistory(uid:String) {
        firestoreDB!!.collection("parkinghistory")
            .whereEqualTo("user",uid)
            .get()
            .addOnCompleteListener { task ->
                if (task.isSuccessful) {
                    val plateEntries = mutableListOf<PlateEntry>()

                    for (doc in task.result!!) {
                        val plateEntry = doc.toObject<PlateEntry>(PlateEntry::class.java)
                        plateEntry.id = doc.id
                        plateEntries.add(plateEntry)
                    }
                    plateEntries.sort()
                    mAdapter = PlateHistoryRecyclerViewAdapter(plateEntries, applicationContext, firestoreDB!!)
                    val mLayoutManager = LinearLayoutManager(applicationContext)

                    rvPlateHistoryList.layoutManager = mLayoutManager
                    rvPlateHistoryList.itemAnimator = DefaultItemAnimator()
                    rvPlateHistoryList.adapter = mAdapter
                } else {
                    Log.d(TAG, "Error getting documents: ", task.exception)
                }
            }
    }
    override fun onBackPressed() {
        if (drawer_layout.isDrawerOpen(GravityCompat.START)) {
            drawer_layout.closeDrawer(GravityCompat.START)
        } else {
            super.onBackPressed()
        }
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        // Inflate the menu; this adds items to the action bar if it is present.
        menuInflater.inflate(R.menu.main, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        when (item.itemId) {
            R.id.action_settings -> return true
            else -> return super.onOptionsItemSelected(item)
        }
    }

    override fun onNavigationItemSelected(item: MenuItem): Boolean {
        // Handle navigation view item clicks here.
        when (item.itemId) {
            R.id.nav_exit -> {
                mAuth!!.signOut()
                val intent = Intent(this, LoginActivity::class.java)
                startActivity(intent)
                return super.onOptionsItemSelected(item)
            }
            R.id.nav_slideshow -> {

            }
            R.id.nav_manage -> {
                if (this.user != null) {
                    val intent = Intent(this, ManagePlatesActivity::class.java)
                    intent.putExtra("uid", this.user)
                    startActivity(intent)
                } else {

                }
            }
            R.id.nav_share -> {

            }
        }

        drawer_layout.closeDrawer(GravityCompat.START)
        return true
    }
}
