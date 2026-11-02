package local.nuvio.catalog;
import android.service.notification.NotificationListenerService;import android.content.*;import android.provider.Settings;import android.util.Log;import java.util.*;
/** Only binding lifecycle is used. Notification payloads are never inspected or stored. */
public class CatalogRevival extends NotificationListenerService {
 public void onListenerConnected(){super.onListenerConnected();try{String old=Settings.Secure.getString(getContentResolver(),Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES);Set<String> services=new LinkedHashSet<>();if(old!=null&&!old.equals("null"))services.addAll(Arrays.asList(old.split(":")));services.add(getPackageName()+"/.CatalogGuard");Settings.Secure.putString(getContentResolver(),Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES,String.join(":",services));Settings.Secure.putInt(getContentResolver(),Settings.Secure.ACCESSIBILITY_ENABLED,1);startForegroundService(new Intent(this,CatalogService.class));Log.i("TVCatalog","Lifecycle rebind restored catalog guard and service");}catch(Exception e){Log.e("TVCatalog","Unable to restore catalog lifecycle",e);}}
 public void onListenerDisconnected(){requestRebind(new ComponentName(this,CatalogRevival.class));}
}
