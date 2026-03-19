package openclaw;

import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.geom.Ellipse2D;
import java.awt.geom.Rectangle2D;

/**
 * A prize (toy) sitting in the pit that the claw can pick up.
 * Each prize is drawn as a coloured circle with a simple face.
 */
public class Prize {

    private double x;
    private double y;
    private final int diameter;
    private final Color color;
    private boolean grabbed;

    public Prize(double x, double y, int diameter, Color color) {
        this.x = x;
        this.y = y;
        this.diameter = diameter;
        this.color = color;
        this.grabbed = false;
    }

    // ── Getters / Setters ────────────────────────────────────────────

    public double getX() { return x; }
    public double getY() { return y; }
    public void setX(double x) { this.x = x; }
    public void setY(double y) { this.y = y; }
    public int getDiameter() { return diameter; }
    public boolean isGrabbed() { return grabbed; }
    public void setGrabbed(boolean grabbed) { this.grabbed = grabbed; }

    /** Centre-point bounding rectangle used for collision checks. */
    public Rectangle2D getBounds() {
        return new Rectangle2D.Double(x, y, diameter, diameter);
    }

    // ── Rendering ────────────────────────────────────────────────────

    public void draw(Graphics2D g) {
        // Body
        g.setColor(color);
        g.fill(new Ellipse2D.Double(x, y, diameter, diameter));

        // Outline
        g.setColor(color.darker());
        g.draw(new Ellipse2D.Double(x, y, diameter, diameter));

        // Simple face – two eyes and a smile
        int cx = (int) x + diameter / 2;
        int cy = (int) y + diameter / 2;
        int eyeSize = Math.max(3, diameter / 8);

        g.setColor(Color.WHITE);
        g.fillOval(cx - diameter / 5 - eyeSize / 2, cy - diameter / 6, eyeSize, eyeSize);
        g.fillOval(cx + diameter / 5 - eyeSize / 2, cy - diameter / 6, eyeSize, eyeSize);

        g.setColor(Color.BLACK);
        int pupil = Math.max(2, eyeSize / 2);
        g.fillOval(cx - diameter / 5 - pupil / 2, cy - diameter / 6, pupil, pupil);
        g.fillOval(cx + diameter / 5 - pupil / 2, cy - diameter / 6, pupil, pupil);

        // Smile arc
        g.drawArc(cx - diameter / 5, cy - diameter / 10, diameter * 2 / 5, diameter / 4, 200, 140);
    }
}
