import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";
import { Name } from "@/types/name";
import { NameLocalization } from "@/lib/name-localization";

interface NamePreviewProps {
  name: Partial<Name>;
  locale?: string;
  className?: string;
}

export function NamePreview({
  name,
  locale = "en-US",
  className,
}: NamePreviewProps) {
  const localization = new NameLocalization(locale);
  const labels = localization.getLabels();

  const formats = {
    "Full Name": localization.formatName(name, "default"),
    "Formal Name": localization.formatName(name, "formal"),
    "Informal Name": localization.formatName(name, "informal"),
  };

  const displayInfo = [
    {
      label: "Preferred Name",
      value: name.preferredName || name.firstName,
      show: true,
    },
    {
      label: "Pronunciation",
      value: name.pronunciation,
      show: !!name.pronunciation,
    },
    {
      label: "Pronouns",
      value: name.pronouns,
      show: !!name.pronouns,
    },
  ];

  return (
    <div className={cn("space-y-4", className)}>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {Object.entries(formats).map(([format, value]) => (
          <Card key={format}>
            <CardContent className="p-4">
              <Label className="block mb-2 text-sm font-medium text-muted-foreground">
                {format}
              </Label>
              <p className="text-lg font-medium">{value || "—"}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardContent className="p-4">
          <Label className="block mb-2 text-sm font-medium text-muted-foreground">
            Display Information
          </Label>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {displayInfo
              .filter((info) => info.show)
              .map((info) => (
                <div key={info.label} className="space-y-1">
                  <p className="text-sm font-medium">{info.label}</p>
                  <p className="text-sm text-muted-foreground">
                    {info.value || "—"}
                  </p>
                </div>
              ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-4">
          <Label className="block mb-2 text-sm font-medium text-muted-foreground">
            All Fields
          </Label>
          <div className="grid grid-cols-2 gap-2 text-sm">
            {Object.entries(name).map(([key, value]) => (
              <div key={key} className="flex justify-between">
                <span className="font-medium">
                  {labels[key as keyof Name]}:
                </span>
                <span className="text-muted-foreground">{value || "—"}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
