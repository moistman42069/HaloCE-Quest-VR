package com.halo.decomp;
import android.graphics.*;
import android.graphics.drawable.*;
import android.widget.Button;

/** Original lightweight orbital artwork; no game artwork or extra texture assets. */
final class LauncherTheme extends Drawable {
    private final Paint paint=new Paint(Paint.ANTI_ALIAS_FLAG);
    @Override public void draw(Canvas canvas) {
        Rect b=getBounds(); float w=b.width(), h=b.height();
        paint.setShader(new LinearGradient(0,0,w,h,new int[]{0xff07121e,0xff122f43,0xff060d16},null,Shader.TileMode.CLAMP));
        canvas.drawRect(b,paint); paint.setShader(null);
        paint.setColor(0xff7499af);
        for(int i=0;i<76;i++) canvas.drawCircle((i*137.51f)%w,(i*97.31f)%h,i%7==0?1.4f:.7f,paint);
        canvas.save(); canvas.rotate(-28,w*.78f,h*.42f);
        RectF ring=new RectF(w*.40f,-h*.65f,w*1.10f,h*1.42f);
        paint.setStyle(Paint.Style.STROKE); paint.setStrokeWidth(w*.065f); paint.setColor(0xff244754); canvas.drawOval(ring,paint);
        paint.setStrokeWidth(w*.005f); paint.setColor(0xff4a7887); canvas.drawOval(ring,paint);
        paint.setStyle(Paint.Style.FILL); canvas.restore();
        paint.setColor(0xa508111b); canvas.drawRect(b,paint);
    }
    static void button(Button button) {
        button.setTextColor(0xffe9f5ff); button.setTextSize(15); button.setLetterSpacing(.09f);
        button.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL)); button.setMinHeight(52);
        StateListDrawable states=new StateListDrawable();
        for(int i=0;i<3;i++) {
            GradientDrawable panel=new GradientDrawable(); panel.setColor(i==2?0xe6192e3d:0xff285674);
            panel.setStroke(1,i==2?0xff517389:0xffb2e1ff); panel.setCornerRadius(3);
            states.addState(i==0?new int[]{android.R.attr.state_pressed}:i==1?new int[]{android.R.attr.state_focused}:new int[]{},panel);
        }
        button.setBackground(states); button.setPadding(16,12,16,12);
    }
    @Override public void setAlpha(int alpha) { }
    @Override public void setColorFilter(ColorFilter filter) { }
    @Override public int getOpacity() { return PixelFormat.OPAQUE; }
}
