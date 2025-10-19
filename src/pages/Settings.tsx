import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { Bell, Globe, Database, Shield, Zap } from "lucide-react";

const Settings = () => {
  return (
    <div className="space-y-8 max-w-4xl">
      {/* Header */}
      <div className="animate-fade-in">
        <h1 className="text-4xl font-bold text-foreground mb-2">
          Settings & Configuration
        </h1>
        <p className="text-muted-foreground">
          Customize your monitoring preferences
        </p>
      </div>

      {/* Data Sources */}
      <div className="rounded-xl bg-card p-6 shadow-md animate-fade-in">
        <div className="flex items-center gap-3 mb-6">
          <div className="rounded-lg bg-primary/10 p-3">
            <Database className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-foreground">
              Data Sources
            </h2>
            <p className="text-sm text-muted-foreground">
              Configure which platforms to monitor
            </p>
          </div>
        </div>

        <div className="space-y-4">
          {["Twitter/X", "Facebook", "Reddit", "Instagram", "LinkedIn", "News Aggregators"].map(
            (source) => (
              <div
                key={source}
                className="flex items-center justify-between p-4 rounded-lg bg-muted/30"
              >
                <Label htmlFor={source} className="cursor-pointer">
                  {source}
                </Label>
                <Switch id={source} defaultChecked />
              </div>
            )
          )}
        </div>
      </div>

      {/* Regional Focus */}
      <div className="rounded-xl bg-card p-6 shadow-md animate-fade-in">
        <div className="flex items-center gap-3 mb-6">
          <div className="rounded-lg bg-accent/10 p-3">
            <Globe className="h-6 w-6 text-accent" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-foreground">
              Regional Focus
            </h2>
            <p className="text-sm text-muted-foreground">
              Select regions to prioritize
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>Primary Region</Label>
            <Select defaultValue="north-america">
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="north-america">North America</SelectItem>
                <SelectItem value="europe">Europe</SelectItem>
                <SelectItem value="asia">Asia</SelectItem>
                <SelectItem value="south-america">South America</SelectItem>
                <SelectItem value="africa">Africa</SelectItem>
                <SelectItem value="global">Global</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Secondary Region</Label>
            <Select defaultValue="europe">
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="north-america">North America</SelectItem>
                <SelectItem value="europe">Europe</SelectItem>
                <SelectItem value="asia">Asia</SelectItem>
                <SelectItem value="south-america">South America</SelectItem>
                <SelectItem value="africa">Africa</SelectItem>
                <SelectItem value="global">Global</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Alert Preferences */}
      <div className="rounded-xl bg-card p-6 shadow-md animate-fade-in">
        <div className="flex items-center gap-3 mb-6">
          <div className="rounded-lg bg-warning/10 p-3">
            <Bell className="h-6 w-6 text-warning" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-foreground">
              Alert Preferences
            </h2>
            <p className="text-sm text-muted-foreground">
              Configure notification settings
            </p>
          </div>
        </div>

        <div className="space-y-6">
          <div className="space-y-4">
            <Label>Alert Sensitivity</Label>
            <Slider defaultValue={[70]} max={100} step={1} />
            <p className="text-xs text-muted-foreground">
              Higher sensitivity = more alerts (Current: 70%)
            </p>
          </div>

          <div className="space-y-4">
            {[
              "Critical misinformation detected",
              "Viral content spreading rapidly",
              "New crisis event identified",
              "Daily summary reports",
            ].map((alert) => (
              <div
                key={alert}
                className="flex items-center justify-between p-4 rounded-lg bg-muted/30"
              >
                <Label htmlFor={alert} className="cursor-pointer">
                  {alert}
                </Label>
                <Switch id={alert} defaultChecked />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* AI Configuration */}
      <div className="rounded-xl bg-card p-6 shadow-md animate-fade-in">
        <div className="flex items-center gap-3 mb-6">
          <div className="rounded-lg bg-success/10 p-3">
            <Zap className="h-6 w-6 text-success" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-foreground">
              AI Configuration
            </h2>
            <p className="text-sm text-muted-foreground">
              Adjust AI analysis parameters
            </p>
          </div>
        </div>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Analysis Frequency</Label>
            <Select defaultValue="realtime">
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="realtime">Real-time</SelectItem>
                <SelectItem value="5min">Every 5 minutes</SelectItem>
                <SelectItem value="15min">Every 15 minutes</SelectItem>
                <SelectItem value="hourly">Hourly</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Confidence Threshold</Label>
            <Select defaultValue="high">
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="low">Low (60%+)</SelectItem>
                <SelectItem value="medium">Medium (75%+)</SelectItem>
                <SelectItem value="high">High (85%+)</SelectItem>
                <SelectItem value="critical">Critical (95%+)</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Security */}
      <div className="rounded-xl bg-card p-6 shadow-md animate-fade-in">
        <div className="flex items-center gap-3 mb-6">
          <div className="rounded-lg bg-critical/10 p-3">
            <Shield className="h-6 w-6 text-critical" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-foreground">
              Security & Privacy
            </h2>
            <p className="text-sm text-muted-foreground">
              Data retention and privacy settings
            </p>
          </div>
        </div>

        <div className="space-y-4">
          {[
            "Enable two-factor authentication",
            "Anonymize user data",
            "Encrypt stored content",
            "Auto-delete old records (90 days)",
          ].map((setting) => (
            <div
              key={setting}
              className="flex items-center justify-between p-4 rounded-lg bg-muted/30"
            >
              <Label htmlFor={setting} className="cursor-pointer">
                {setting}
              </Label>
              <Switch id={setting} defaultChecked />
            </div>
          ))}
        </div>
      </div>

      {/* Save Button */}
      <div className="flex gap-4 justify-end">
        <Button variant="outline">Reset to Defaults</Button>
        <Button className="bg-gradient-primary">Save Changes</Button>
      </div>
    </div>
  );
};

export default Settings;
