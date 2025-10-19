import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useState } from "react";
import { Target, Users, Radio, FileText, Edit, Save } from "lucide-react";

const recommendations = [
  {
    id: 1,
    category: "Government Response",
    icon: Target,
    items: [
      "Issue official statement clarifying policy within 2 hours",
      "Coordinate with fact-checking organizations",
      "Prepare press briefing with verified data",
    ],
  },
  {
    id: 2,
    category: "Media Strategy",
    icon: Radio,
    items: [
      "Distribute official narrative to trusted media outlets",
      "Provide journalists with fact-check resources",
      "Monitor media coverage and respond to inaccuracies",
    ],
  },
  {
    id: 3,
    category: "Public Engagement",
    icon: Users,
    items: [
      "Launch social media campaign with verified information",
      "Engage community leaders and influencers",
      "Create shareable infographics debunking misinformation",
    ],
  },
];

const counterNarratives = [
  {
    id: 1,
    title: "Official Statement Template",
    content: "Based on verified sources and expert analysis, the facts are as follows...",
    confidence: 92,
  },
  {
    id: 2,
    title: "Social Media Response",
    content: "We've fact-checked this claim. Here's what you need to know...",
    confidence: 88,
  },
  {
    id: 3,
    title: "Community Outreach Message",
    content: "Working together, we can counter misinformation by sharing verified information...",
    confidence: 85,
  },
];

const Strategy = () => {
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editedContent, setEditedContent] = useState("");

  const handleEdit = (id: number, content: string) => {
    setEditingId(id);
    setEditedContent(content);
  };

  const handleSave = () => {
    setEditingId(null);
    // In a real app, this would save to backend
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="animate-fade-in">
        <h1 className="text-4xl font-bold text-foreground mb-2">
          Response Strategy
        </h1>
        <p className="text-muted-foreground">
          AI-generated recommendations and counter-narratives
        </p>
      </div>

      {/* Action Recommendations */}
      <div className="space-y-4">
        <h2 className="text-2xl font-semibold text-foreground">
          Recommended Actions
        </h2>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {recommendations.map((rec) => (
            <div
              key={rec.id}
              className="rounded-xl bg-card p-6 shadow-md hover:shadow-lg transition-all duration-200 animate-fade-in"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="rounded-lg bg-primary/10 p-3">
                  <rec.icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-lg font-semibold text-foreground">
                  {rec.category}
                </h3>
              </div>
              <ul className="space-y-3">
                {rec.items.map((item, index) => (
                  <li
                    key={index}
                    className="flex items-start gap-2 text-sm text-muted-foreground"
                  >
                    <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-primary flex-shrink-0" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* Counter-Narratives */}
      <div className="space-y-4">
        <h2 className="text-2xl font-semibold text-foreground">
          Counter-Narrative Templates
        </h2>
        <div className="space-y-4">
          {counterNarratives.map((narrative) => (
            <div
              key={narrative.id}
              className="rounded-xl bg-card p-6 shadow-md hover:shadow-lg transition-all duration-200 animate-fade-in"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-accent/10 p-2">
                    <FileText className="h-5 w-5 text-accent" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-foreground">
                      {narrative.title}
                    </h3>
                    <p className="text-sm text-primary">
                      {narrative.confidence}% effectiveness score
                    </p>
                  </div>
                </div>
                {editingId !== narrative.id ? (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleEdit(narrative.id, narrative.content)}
                  >
                    <Edit className="h-4 w-4 mr-2" />
                    Edit
                  </Button>
                ) : (
                  <Button
                    size="sm"
                    onClick={handleSave}
                    className="bg-gradient-primary"
                  >
                    <Save className="h-4 w-4 mr-2" />
                    Save
                  </Button>
                )}
              </div>

              {editingId === narrative.id ? (
                <Textarea
                  value={editedContent}
                  onChange={(e) => setEditedContent(e.target.value)}
                  className="min-h-[100px]"
                />
              ) : (
                <p className="text-muted-foreground">{narrative.content}</p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 justify-end">
        <Button variant="outline">
          Export All Templates
        </Button>
        <Button className="bg-gradient-primary">
          Deploy Strategy
        </Button>
      </div>
    </div>
  );
};

export default Strategy;
