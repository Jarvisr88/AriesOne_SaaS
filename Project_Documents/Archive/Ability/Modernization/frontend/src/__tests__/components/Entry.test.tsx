import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import { Entry } from "@/components/entry/Entry";
import { commonValidations, createNumberFormatter } from "@/types/entry";
import { z } from "zod";

describe("Entry Component", () => {
  it("renders with basic props", () => {
    render(
      <Entry<string>
        initialValue="test"
        label="Test Input"
        placeholder="Enter text"
      />
    );

    expect(screen.getByLabelText("Test Input")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Enter text")).toBeInTheDocument();
    expect(screen.getByDisplayValue("test")).toBeInTheDocument();
  });

  it("handles required validation", async () => {
    const onValidate = vi.fn();
    render(
      <Entry<string>
        label="Required Input"
        required
        validation={[commonValidations.required()]}
        onValidate={onValidate}
      />
    );

    const input = screen.getByLabelText("Required Input");
    await userEvent.clear(input);
    await userEvent.tab();

    expect(screen.getByText("This field is required")).toBeInTheDocument();
    expect(onValidate).toHaveBeenCalledWith(false);
  });

  it("handles number formatting", async () => {
    const formatter = createNumberFormatter("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });

    const onChange = vi.fn();
    render(
      <Entry<number>
        initialValue={1234.5}
        label="Number Input"
        formatter={formatter}
        onChange={onChange}
      />
    );

    const input = screen.getByLabelText("Number Input");
    expect(input).toHaveValue("1,234.50");

    await userEvent.clear(input);
    await userEvent.type(input, "4567.89");
    await userEvent.tab();

    expect(input).toHaveValue("4,567.89");
    expect(onChange).toHaveBeenCalledWith(4567.89);
  });

  it("handles Zod schema validation", async () => {
    const schema = z.string().email("Invalid email format");
    const onValidate = vi.fn();

    render(
      <Entry<string>
        label="Email Input"
        schema={schema}
        onValidate={onValidate}
      />
    );

    const input = screen.getByLabelText("Email Input");
    await userEvent.type(input, "invalid-email");
    await userEvent.tab();

    expect(screen.getByText("Invalid email format")).toBeInTheDocument();
    expect(onValidate).toHaveBeenCalledWith(false);

    await userEvent.clear(input);
    await userEvent.type(input, "valid@email.com");
    await userEvent.tab();

    expect(screen.queryByText("Invalid email format")).not.toBeInTheDocument();
    expect(onValidate).toHaveBeenCalledWith(true);
  });

  it("handles disabled state", () => {
    render(
      <Entry<string>
        initialValue="test"
        label="Disabled Input"
        disabled
      />
    );

    expect(screen.getByLabelText("Disabled Input")).toBeDisabled();
  });

  it("handles readonly state", () => {
    render(
      <Entry<string>
        initialValue="test"
        label="Readonly Input"
        readOnly
      />
    );

    expect(screen.getByLabelText("Readonly Input")).toHaveAttribute("readonly");
  });

  it("displays tooltip", async () => {
    render(
      <Entry<string>
        label="Input with Tooltip"
        tooltip="Helper text"
      />
    );

    const tooltipTrigger = screen.getByRole("button");
    await userEvent.hover(tooltipTrigger);

    await waitFor(() => {
      expect(screen.getByText("Helper text")).toBeInTheDocument();
    });
  });

  it("handles custom validation", async () => {
    const customValidation = {
      validate: (value: string) => value.length >= 5,
      message: "Must be at least 5 characters",
    };

    render(
      <Entry<string>
        label="Custom Validation"
        validation={[customValidation]}
      />
    );

    const input = screen.getByLabelText("Custom Validation");
    await userEvent.type(input, "test");
    await userEvent.tab();

    expect(screen.getByText("Must be at least 5 characters")).toBeInTheDocument();

    await userEvent.type(input, "y");
    await userEvent.tab();

    expect(screen.queryByText("Must be at least 5 characters")).not.toBeInTheDocument();
  });

  it("handles multiple validations", async () => {
    const validations = [
      commonValidations.required("Field is required"),
      commonValidations.minLength(3, "Too short"),
      commonValidations.pattern(/^[A-Z]/, "Must start with uppercase"),
    ];

    render(
      <Entry<string>
        label="Multiple Validations"
        validation={validations}
      />
    );

    const input = screen.getByLabelText("Multiple Validations");
    await userEvent.tab();
    expect(screen.getByText("Field is required")).toBeInTheDocument();

    await userEvent.type(input, "a");
    await userEvent.tab();
    expect(screen.getByText("Too short")).toBeInTheDocument();

    await userEvent.clear(input);
    await userEvent.type(input, "abc");
    await userEvent.tab();
    expect(screen.getByText("Must start with uppercase")).toBeInTheDocument();

    await userEvent.clear(input);
    await userEvent.type(input, "Abc");
    await userEvent.tab();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });
});
