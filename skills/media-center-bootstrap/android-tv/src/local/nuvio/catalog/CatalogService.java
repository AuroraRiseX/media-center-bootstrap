package local.nuvio.catalog;
import android.app.*;import android.os.*;import android.content.*;import android.util.Log;
public class CatalogService extends Service {
 CatalogServer server;
 public void onCreate(){super.onCreate();NotificationManager n=getSystemService(NotificationManager.class);n.createNotificationChannel(new NotificationChannel("catalog","电视本机目录服务",NotificationManager.IMPORTANCE_LOW));startForeground(1,new Notification.Builder(this,"catalog").setSmallIcon(android.R.drawable.ic_menu_gallery).setContentTitle("Nuvio 中文目录运行中").setContentText("目录及图片由本电视提供，无需 Mac").build());new Thread(()->{try{server=new CatalogServer(this);server.run();}catch(Exception e){Log.e("TVCatalog","Server failed",e);stopSelf();}},"catalog-listener").start();}
 public int onStartCommand(Intent i,int f,int id){return START_STICKY;} public IBinder onBind(Intent i){return null;}public void onDestroy(){if(server!=null)server.close();super.onDestroy();}
}
