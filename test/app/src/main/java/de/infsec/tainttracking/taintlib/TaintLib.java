package app.src.main.java.de.infsec.tainttracking.taintlib;


import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.util.Log;
import android.widget.Toast;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.HashMap;
import java.util.Stack;

public class TaintLib {
    public static TaintLib instance = new TaintLib();

    private static final String TAG = "ArtistLib";
    private static final String VERSION = TAG + " # 1.0.0";


    private static int checkPermissionCounter = 0;

    private static final String LEAKAGE_NOTIFICATION =
            "ALARM! Private Data (Tainted value) is about to leak!";

    private static final String PERMISSIONS_OK = "MethodCall is allowed!";
    private static final String PERMISSIONS_ERROR= "MethodCall is not allowed!";

    private static final String PERMISSIONS_NOTIFICATION =
            "Permission Protected Method is Called!";

    public  boolean leakOccured = false;

    public enum PermissionId {
        NO_PERMISSION(-1),
        ACCESS_COARSE_LOCATION(0),
        ACCESS_FINE_LOCATION(1),
        ACCESS_WIFI_STATE(2),
        BLUETOOTH(3),
        BLUETOOTH_ADMIN(4),
        READ_PHONE_STATE(5);

        private final int id;

        PermissionId(final int id) {
            this.id = id;
        }
        public int getValue() {
            return this.id;
        }
    };

    static boolean PERMISSION_MAP[];

    static volatile int additionResult = 0;

    private TaintLib() {
        Log.v(TAG, "TaintLib() " + VERSION);
    }

    static {
        PERMISSION_MAP = new boolean[6];
        PERMISSION_MAP[0] = true;
        PERMISSION_MAP[1] = true;
        PERMISSION_MAP[2] = true;
        PERMISSION_MAP[3] = true;
        PERMISSION_MAP[4] = true;
        PERMISSION_MAP[5] = true;
    }

    //TODO different maps for static and instance fields to decrease the chance of collisions? (keys are computed differently)
    private HashMap<Long, Boolean> taintMap = new HashMap<>();


    private final ThreadLocal<Stack<Boolean>> argTaintStack = new ThreadLocal<Stack<Boolean>>() {
        @Override
        protected Stack<Boolean> initialValue() {
            return new Stack<>();
        }
    };
    private final ThreadLocal<Boolean> resultTaintMarker = new ThreadLocal<Boolean>() {
        @Override
        protected Boolean initialValue() {
            return false;
        }
    };

    public long createInstanceFieldKey(Object o, int fieldID) {
        Log.d(TAG, "createInstanceFieldKey");
        long result = (((long)System.identityHashCode(o))<<32) + fieldID;
        return result;
    }

    public void setArgTaint(boolean taint) {
        Log.d(TAG, "ARG push: " + taint);
        argTaintStack.get().push(taint);
    }

    public boolean getArgTaint() {
        Log.d(TAG, "getArgTaint");
        Stack<Boolean> ts = argTaintStack.get();
        if(ts.isEmpty()) {
            return false;
        }
        boolean argtaint = ts.pop();
        Log.d(TAG, "ARG pop: " + argtaint);
        return argtaint;
    }

    public void setReturnTaint(boolean taint) {
        Log.d(TAG, "RET push: "+taint);
        //taintStack.get().push(taint);
        resultTaintMarker.set(taint);
    }

    public boolean getReturnTaint() {
        boolean taint = resultTaintMarker.get();
        Log.d(TAG, "RET pop: " + taint);
        return taint;
    }

    public void setFieldTaint(long key, boolean taint) {
        Log.d(TAG, "FIELD set("+key+"): "+taint);
        taintMap.put(key, taint);
    }
    public boolean getFieldTaint(long key) {
        Boolean taint = taintMap.get(key);
        Log.d(TAG, "FIELD get(" + key + "): " + taint);
        if(taint !=null) {
            return taint;
        } else {
            return false;
        }
    }

    public boolean combineTaint(boolean taint1, boolean taint2) {
        Log.d(TAG, "combineTaint: " + taint1 + " || " + taint2 + " -> " + (taint1 || taint2));
        return taint1 || taint2;
    }

    public void checkLeakage(boolean taintValue) {

        leakOccured = taintValue;

        if(taintValue) {
            notifyUserOfLeakage();
        } else {
            Log.d(TAG, "No leakage here since value is not tainted");
        }
    }

    public void checkPermission() {
        Log.d(TAG, "checkPermission()");

        notifyViaApp(PERMISSIONS_NOTIFICATION);
        Log.d(TAG, PERMISSIONS_NOTIFICATION);

        Log.d(TAG, "checkPermission() DONE");
    }

    public void checkPermission(final int permissionId) {

        ++checkPermissionCounter;

        if (permissionId >= PERMISSION_MAP.length) {
            Log.d(TAG, "checkPermission() ERROR: permissionId " + permissionId +
                       " PERMISSION_MAP Size:" + PERMISSION_MAP.length);
            return;
        }

        boolean permissionOk = PERMISSION_MAP[permissionId];

        String PERMISSION_NAME = "NOT FOUND";
        for (PermissionId permid : PermissionId.values()) {
            if (permid.getValue() == permissionId) {
                PERMISSION_NAME = permid.toString();
                break;
            }
        }

        if (checkPermissionCounter % 10000 == 0) {
            Log.d(TAG, "checkPermission() checkPermissionCount #" + checkPermissionCounter);
        }

        if (permissionOk) {
            additionResult = 5 + permissionId;
        } else {
            throw new SecurityException("Permission is missing: " + PERMISSION_NAME);
        }
    }

    public void checkPermissionVisual(final int permissionId) {
        Log.d(TAG, "checkPermissionVisual()");
        Log.d(TAG, "checkPermissionVisual() permissionId: " + permissionId);

        if (permissionId >= PERMISSION_MAP.length) {
            Log.d(TAG, "checkPermissionVisual() ERROR: permissionId " + permissionId +
                    " PERMISSION_MAP Size:" + PERMISSION_MAP.length);
        }

        boolean permissionOk = PERMISSION_MAP[permissionId];

        String PERMISSION_NAME = "NOT FOUND";
        for (PermissionId permid : PermissionId.values()) {
            if (permid.getValue() == permissionId) {
                PERMISSION_NAME = permid.toString();
                break;
            }
        }

        Log.d(TAG, "checkPermissionVisual() Permission Needed: android.permission." + PERMISSION_NAME);

        if (permissionOk) {
            Log.d(TAG, PERMISSIONS_OK);
        } else {
            Log.d(TAG, PERMISSIONS_ERROR);
        }

        Log.d(TAG, "checkPermissionVisual() DONE");
    }

    private void notifyUserOfLeakage() {
        Log.d(TAG, "notifyUserOfLeakage()");
        // final Context context = getActivityThreadContext();
        // final Context context = getApplicationContext();
        // notifyViaToast(context, LEAKAGE_NOTIFICATION);
        // notifyViaDialog(context, LEAKAGE_NOTIFICATION);
        notifyViaApp(LEAKAGE_NOTIFICATION);
        Log.d(TAG, LEAKAGE_NOTIFICATION);
        Log.d(TAG, "notifyUserOfLeakage() DONE")     ;
    }

    /** Needs a valid Context aware this-pointer to an activity.
     *
     * @param context
     * @param leak_notification
     */
    private void notifyViaDialog(final Context context, final String leak_notification) {
        final AlertDialog.Builder builder = new AlertDialog.Builder(context);
        builder.setMessage("ALARM!!! Tainted value is about to leak!!!").setTitle("Leakage Detected!");
        builder.setNeutralButton("Ok", new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialog, int id) {
                Log.d(TAG, "User clicked OK");
            }
        });
        final AlertDialog dialog = builder.create();
        dialog.show();
    }

    /** Needs the application context.
     *  No Acitivty this pointer is needed.
     *
     *  Works with #getActivityThreadContext()
     *
     * @param context
     * @param LEAK_NOTIFICATION
     */
    private void notifyViaToast(final Context context, final String LEAK_NOTIFICATION) {
        final int TOAST_DURATION = Toast.LENGTH_LONG;
        Toast toast = Toast.makeText(context, LEAK_NOTIFICATION, TOAST_DURATION);
        toast.show();
    }

    /** Calls the notifyViaDialog function in the app that has the tainlib injected.
     *  Dialogs need a this pointer aka activity pointer, that the WindowManager stays
     *  happy.
     *  => This is a workaround solution, a proper Dialog Creator is need.
     *  Possibilities include an own lightweight Activity,
     *  Notifications and more.
     *
     */
    private void notifyViaApp(final String LEAK_NOTIFICATION) {
        Log.d(TAG, "notifyViaApp()");
        final String CLASS_WITH_CONTEXT_METHOD = "de.infsec.taintleak.MainActivity";
        final String _M_GET_NOTIFY_VIA_DIALOG = "notifyViaDialog";

        try {
            Class<?> taintLeakMainActivity = Class.forName(CLASS_WITH_CONTEXT_METHOD);

            final Method[] taintLeakMethods = taintLeakMainActivity.getDeclaredMethods();
            for (Method method : taintLeakMethods) {
                final String methodName = method.getName();
                // Skipping everything except our wanted method
                if (!methodName.startsWith(_M_GET_NOTIFY_VIA_DIALOG)) {
                    continue;
                }
                try {
                    // Invoking static method, therefore null
                    final Object returnValue = method.invoke(null, new String(LEAK_NOTIFICATION));
                    Log.d(TAG, CLASS_WITH_CONTEXT_METHOD + "."
                            + _M_GET_NOTIFY_VIA_DIALOG + " executed: " + (Boolean)returnValue);
                    break;
                } catch (final InvocationTargetException e) {
                    Log.e(TAG, "Invokation Failed for " + method.getName(), e);
                }
            }

        } catch (final Exception e) {
            Log.d(TAG, "ERROR notifyViaApp() Did not get Apps context ", e);
        }
        Log.d(TAG, "notifyViaApp() DONE");
    }

    /*
    Used during benchmarking for fast teardown.
     */
    public void resetTaintInfo() {
        argTaintStack.get().clear();
        resultTaintMarker.set(false);
        taintMap.clear();
        leakOccured = false;
    }

    public void traceLog() {
        StackTraceElement[] stackTrace = Thread.currentThread().getStackTrace();
        try {
            StackTraceElement callingMethod = stackTrace[3];
            android.util.Log.d(TAG, "TRACE: " + callingMethod.toString());
        } catch (final NullPointerException e) {
            android.util.Log.d(TAG, "traceLog() ", e);
        } catch (final ArrayIndexOutOfBoundsException e) {
            android.util.Log.d(TAG, "traceLog() ", e);
        }
    }

    public void logHello() {
        StackTraceElement[] stackTrace = Thread.currentThread().getStackTrace();
        try {
            StackTraceElement callingMethod = stackTrace[3];
            android.util.Log.d(TAG, "CALLER: " + callingMethod.toString());
        } catch (final NullPointerException e) {
            android.util.Log.d(TAG, "HelloInjection() ", e);
        } catch (final ArrayIndexOutOfBoundsException e) {
            android.util.Log.d(TAG, "HelloInjection() ", e);
        }
    }

    public static void logHelloStatic() {
        StackTraceElement[] stackTrace = Thread.currentThread().getStackTrace();
        try {
            StackTraceElement callingMethod = stackTrace[3];
            android.util.Log.d(TAG, "CALLER: " + callingMethod.toString());
        } catch (final NullPointerException e) {
            android.util.Log.d(TAG, "HelloStaticInjection() ", e);
        } catch (final ArrayIndexOutOfBoundsException e) {
            android.util.Log.d(TAG, "HelloStaticInjection() ", e);
        }
    }

    public void logHelloBoolean(boolean value) {
        android.util.Log.d(TAG, "HelloInjection() boolen: " + value);
        StackTraceElement[] stackTrace = Thread.currentThread().getStackTrace();
        try {
            StackTraceElement callingMethod = stackTrace[3];
            android.util.Log.d(TAG, "HelloInjection() CALLER: " + callingMethod.toString());
        } catch (final NullPointerException e) {
            android.util.Log.d(TAG, "HelloInjection() ", e);
        } catch (final ArrayIndexOutOfBoundsException e) {
            android.util.Log.d(TAG, "HelloInjection() ", e);
        }
    }

    public void logHelloInt(int value) {
        android.util.Log.d(TAG, "HelloInjection() int: " + value);
        StackTraceElement[] stackTrace = Thread.currentThread().getStackTrace();
        try {
            StackTraceElement callingMethod = stackTrace[3];
            android.util.Log.d(TAG, "HelloInjection() CALLER: " + callingMethod.toString());
        } catch (final NullPointerException e) {
            android.util.Log.d(TAG, "HelloInjection() ", e);
        } catch (final ArrayIndexOutOfBoundsException e) {
            android.util.Log.d(TAG, "HelloInjection() ", e);
        }
    }

    public void logHelloLong(long value) {
        android.util.Log.d(TAG, "HelloInjection() long: " + value);
        StackTraceElement[] stackTrace = Thread.currentThread().getStackTrace();
        try {
            StackTraceElement callingMethod = stackTrace[3];
            android.util.Log.d(TAG, "HelloInjection() CALLER: " + callingMethod.toString());
        } catch (final NullPointerException e) {
            android.util.Log.d(TAG, "HelloInjection() ", e);
        } catch (final ArrayIndexOutOfBoundsException e) {
            android.util.Log.d(TAG, "HelloInjection() ", e);
        }
    }

    public void logHelloIntInt(int value, int value2) {
        android.util.Log.d(TAG, "HelloInjection() int: " + value + " int2: " + value2);
        StackTraceElement[] stackTrace = Thread.currentThread().getStackTrace();
        try {
            StackTraceElement callingMethod = stackTrace[3];
            android.util.Log.d(TAG, "HelloInjection() CALLER: " + callingMethod.toString());
        } catch (final NullPointerException e) {
            android.util.Log.d(TAG, "HelloInjection() ", e);
        } catch (final ArrayIndexOutOfBoundsException e) {
            android.util.Log.d(TAG, "HelloInjection() ", e);
        }
    }
    public void logHelloLongBoolean(long value, boolean value2) {
        android.util.Log.d(TAG, "HelloInjection() long: " + value + " boolean: " + value2);
        StackTraceElement[] stackTrace = Thread.currentThread().getStackTrace();
        try {
            StackTraceElement callingMethod = stackTrace[3];
            android.util.Log.d(TAG, "HelloInjection() CALLER: " + callingMethod.toString());
        } catch (final NullPointerException e) {
            android.util.Log.d(TAG, "HelloInjection() ", e);
        } catch (final ArrayIndexOutOfBoundsException e) {
            android.util.Log.d(TAG, "HelloInjection() ", e);
        }
    }

    public void logHelloObjectInt(Object value, int value2) {
        android.util.Log.d(TAG, "HelloInjection() object: " + value.toString() + " int: " + value2);
        StackTraceElement[] stackTrace = Thread.currentThread().getStackTrace();
        try {
            StackTraceElement callingMethod = stackTrace[3];
            android.util.Log.d(TAG, "HelloInjection() CALLER: " + callingMethod.toString());
        } catch (final NullPointerException e) {
            android.util.Log.d(TAG, "HelloInjection() ", e);
        } catch (final ArrayIndexOutOfBoundsException e) {
            android.util.Log.d(TAG, "HelloInjection() ", e);
        }
    }



    private Context getApplicationContext() {
        final String CLASS_WITH_CONTEXT_METHOD = "de.infsec.taintleak.MainActivity";
        final String _M_GET_CONTEXT = "getContext";

        Context context = null;
        try {
            Class<?> taintLeakMainActivity = Class.forName(CLASS_WITH_CONTEXT_METHOD);

            final Method[] taintLeakMethods = taintLeakMainActivity.getDeclaredMethods();
            for (Method method : taintLeakMethods) {
                final String methodName = method.getName();
                // Skipping everythinf except our wanted method
                if (!methodName.startsWith(_M_GET_CONTEXT)
                        || (method.getGenericReturnType() != boolean.class)) {
                    continue;
                }
                try {
                    method.setAccessible(true);
                    // Invoking static method, therefore null
                    final Object appContext = method.invoke(null);
                    context = (Context) appContext;
                    break;
                } catch (final InvocationTargetException e) {
                    Log.e(TAG, "Invokation Failed for " + method.getName(), e);
                }
            }

        } catch (final Exception e) {
            Log.d(TAG, "ERROR getApplicationContext() Did not get Apps context ", e);
        }
        return context;
    }

    /** Only suitable for Alarms, fails for Dialogs:
     *
     * * WindowManager: Attempted to add window with non-application token WindowToken{77cff9b null}.  Aborting.
     *   => Fix not investigated
     *
     *
     * @return
     */
    private static Context getActivityThreadContext() {
        Context context = null;
        try {
            Class<?> activityThreadClass = Class.forName("android.app.ActivityThread");
            Class[] params = new Class[0];
            Method currentActivityThread = activityThreadClass.getDeclaredMethod("currentActivityThread", params);
            Boolean accessible = currentActivityThread.isAccessible();
            currentActivityThread.setAccessible(true);
            Object object = currentActivityThread.invoke(activityThreadClass);
            if (object == null) {
                Log.d("ERROR", "The current activity thread is null!");
                return null;
            }
            currentActivityThread.setAccessible(accessible);
            Method getSystemContext = activityThreadClass.getDeclaredMethod("getSystemContext", params);
            accessible = getSystemContext.isAccessible();
            getSystemContext.setAccessible(true);
            context = (Context) getSystemContext.invoke(object);
            getSystemContext.setAccessible(accessible);
        } catch (final Exception e) {
            Log.d(TAG, "ERROR: ", e);
        }
        return context;
    }
}
