import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { AddressForm } from "./AddressForm";
import { Address } from "@/types/address";
import { MapPin } from "lucide-react";

interface AddressInputProps {
  value?: Address;
  onChange: (address: Address) => void;
  readOnly?: boolean;
  className?: string;
}

export function AddressInput({
  value,
  onChange,
  readOnly = false,
  className,
}: AddressInputProps) {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isValid, setIsValid] = useState(true);

  const handleAddressChange = (newAddress: Address) => {
    onChange(newAddress);
  };

  const formatAddress = (address?: Address) => {
    if (!address) return "No address selected";
    const parts = [
      address.street1,
      address.street2,
      address.city,
      address.state,
      address.zipCode,
    ].filter(Boolean);
    return parts.join(", ");
  };

  return (
    <div className={className}>
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogTrigger asChild>
          <Button
            variant="outline"
            className="w-full justify-start text-left font-normal"
            disabled={readOnly}
          >
            <MapPin className="mr-2 h-4 w-4" />
            <span className="truncate">{formatAddress(value)}</span>
          </Button>
        </DialogTrigger>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Enter Address</DialogTitle>
          </DialogHeader>
          <AddressForm
            value={value}
            onChange={handleAddressChange}
            onValidate={setIsValid}
            readOnly={readOnly}
          />
        </DialogContent>
      </Dialog>
    </div>
  );
}
