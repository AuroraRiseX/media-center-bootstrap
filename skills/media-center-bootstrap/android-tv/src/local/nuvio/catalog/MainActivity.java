package local.nuvio.catalog;
import android.app.*;import android.os.*;import android.content.*;import android.widget.*;
public class MainActivity extends Activity {
 public void onCreate(Bundle b){super.onCreate(b);startForegroundService(new Intent(this,CatalogService.class)); LinearLayout l=new LinearLayout(this);l.setOrientation(1);l.setPadding(70,65,70,40); TextView t=new TextView(this);t.setText("Nuvio 电视目录\n\n目录、中文资料与分类封面运行在本电视。\n地址：http://127.0.0.1:17863\n无需 Mac 开机，仍需网络访问影视资料库。\n\n服务会随电视启动。请勿强行停止或卸载本应用。");t.setTextSize(23);l.addView(t);Button btn=new Button(this);btn.setText("打开 Nuvio");btn.setOnClickListener(v->{Intent i=getPackageManager().getLaunchIntentForPackage("com.nuvio.tv");if(i!=null)startActivity(i);});l.addView(btn);setContentView(l); }
}
