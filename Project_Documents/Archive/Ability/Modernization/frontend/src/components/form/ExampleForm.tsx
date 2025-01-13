import React from "react";
import { z } from "zod";
import { Form } from "./Form";
import { Entry } from "@/components/entry/Entry";
import { Button } from "@/components/ui/button";
import {
  commonValidations,
  createNumberFormatter,
  createDateFormatter,
  createCurrencyFormatter,
} from "@/types/entry";

const schema = z.object({
  firstName: z.string().min(2, "First name must be at least 2 characters"),
  lastName: z.string().min(2, "Last name must be at least 2 characters"),
  email: z.string().email("Invalid email address"),
  age: z.number().min(18, "Must be at least 18 years old"),
  salary: z.number().min(0, "Salary cannot be negative"),
  birthDate: z.date(),
  phone: z.string(),
});

type FormValues = z.infer<typeof schema>;

const initialValues: FormValues = {
  firstName: "",
  lastName: "",
  email: "",
  age: 0,
  salary: 0,
  birthDate: new Date(),
  phone: "",
};

interface ExampleFormProps {
  onSubmit: (values: FormValues) => Promise<void>;
  onError?: (errors: Record<string, string>) => void;
}

export function ExampleForm({ onSubmit, onError }: ExampleFormProps) {
  return (
    <Form
      onSubmit={onSubmit}
      onError={onError}
      initialValues={initialValues}
      className="max-w-md mx-auto"
    >
      <Entry<string>
        name="firstName"
        label="First Name"
        required
        schema={schema.shape.firstName}
        validation={[commonValidations.required()]}
        tooltip="Enter your legal first name"
      />

      <Entry<string>
        name="lastName"
        label="Last Name"
        required
        schema={schema.shape.lastName}
        validation={[commonValidations.required()]}
        tooltip="Enter your legal last name"
      />

      <Entry<string>
        name="email"
        label="Email"
        type="email"
        required
        schema={schema.shape.email}
        validation={[
          commonValidations.required(),
          commonValidations.email(),
        ]}
        tooltip="Enter your business email address"
      />

      <Entry<number>
        name="age"
        label="Age"
        type="number"
        required
        schema={schema.shape.age}
        formatter={createNumberFormatter()}
        validation={[
          commonValidations.required(),
          commonValidations.min(18),
          commonValidations.max(120),
        ]}
        tooltip="You must be at least 18 years old"
      />

      <Entry<number>
        name="salary"
        label="Expected Salary"
        required
        schema={schema.shape.salary}
        formatter={createCurrencyFormatter()}
        validation={[
          commonValidations.required(),
          commonValidations.min(0),
        ]}
        tooltip="Enter your expected annual salary"
      />

      <Entry<Date>
        name="birthDate"
        label="Date of Birth"
        type="date"
        required
        schema={schema.shape.birthDate}
        formatter={createDateFormatter()}
        validation={[
          commonValidations.required(),
        ]}
        tooltip="Enter your date of birth"
      />

      <Entry<string>
        name="phone"
        label="Phone Number"
        type="tel"
        required
        schema={schema.shape.phone}
        validation={[
          commonValidations.required(),
          commonValidations.phone(),
        ]}
        tooltip="Enter your contact phone number"
      />

      <div className="flex justify-end gap-4 pt-4">
        <Button type="reset" variant="outline">
          Reset
        </Button>
        <Button type="submit">
          Submit
        </Button>
      </div>
    </Form>
  );
}
