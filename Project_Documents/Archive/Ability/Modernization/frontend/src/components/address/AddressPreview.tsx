import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";
import { Address } from "@/types/address";
import { AddressLocalization } from "@/lib/address-localization";

interface AddressPreviewProps {
  address: Partial<Address>;
  locale?: string;
  className?: string;
}

export function AddressPreview({
  address,
  locale = "en-US",
  className,
}: AddressPreviewProps) {
  const localization = new AddressLocalization(locale);
  const formattedAddress = localization.formatAddress(address);
  const labels = localization.getLabels();

  const formats = {
    "Default": formattedAddress,
    "Single Line": formattedAddress.replace(/\n/g, ", "),
    "HTML": formattedAddress.replace(/\n/g, "<br>"),
    "JSON": JSON.stringify(address, null, 2),
  };

  return (
    <div className={cn("space-y-4", className)}>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(formats).map(([format, value]) => (
          <Card key={format} className="overflow-hidden">
            <CardContent className="p-4">
              <Label className="block mb-2 text-sm font-medium text-muted-foreground">
                {format} Format
              </Label>
              {format === "JSON" ? (
                <pre className="bg-muted p-2 rounded-md text-xs overflow-x-auto">
                  {value}
                </pre>
              ) : format === "HTML" ? (
                <pre className="bg-muted p-2 rounded-md text-xs overflow-x-auto whitespace-pre-wrap">
                  {value}
                </pre>
              ) : (
                <p
                  className={cn(
                    "text-sm",
                    format === "Single Line" && "truncate"
                  )}
                >
                  {value}
                </p>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardContent className="p-4">
          <Label className="block mb-2 text-sm font-medium text-muted-foreground">
            Field Values
          </Label>
          <div className="grid grid-cols-2 gap-2 text-sm">
            {Object.entries(address)
              .filter(([key]) => key !== "placeId" && key !== "formattedAddress")
              .map(([key, value]) => (
                <div key={key} className="flex justify-between">
                  <span className="font-medium">
                    {labels[key as keyof Address]}:
                  </span>
                  <span className="text-muted-foreground">{value}</span>
                </div>
              ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
