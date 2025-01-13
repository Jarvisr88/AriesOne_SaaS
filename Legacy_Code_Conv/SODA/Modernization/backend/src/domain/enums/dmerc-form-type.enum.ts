/**
 * Represents the different types of DMERC (Durable Medical Equipment Regional Carrier) forms.
 * Each form type has a specific version and purpose in DME documentation.
 */
export enum DmercFormType {
  // Oxygen and PAP forms
  DMERC_0102A = '01.02A', // Oxygen CMN
  DMERC_0102B = '01.02B', // PAP Devices
  
  // Pneumatic Compression and Support Surfaces
  DMERC_0203A = '02.03A', // Pneumatic Compression
  DMERC_0203B = '02.03B', // Support Surfaces
  
  // Manual Wheelchairs
  DMERC_0302 = '03.02',   // Manual Wheelchairs
  
  // Power Mobility Devices
  DMERC_0403B = '04.03B', // Power Wheelchairs
  DMERC_0403C = '04.03C', // Power Operated Vehicles
  
  // Enteral and Parenteral Nutrition
  DMERC_0602B = '06.02B', // Enteral Nutrition
  
  // Osteogenesis Stimulators
  DMERC_0702A = '07.02A', // Osteogenesis Stimulators
  DMERC_0702B = '07.02B', // Spinal Cord Stimulators
  
  // External Infusion Pumps
  DMERC_0802 = '08.02',   // External Infusion Pumps
  
  // Orthoses and Prostheses
  DMERC_0902 = '09.02',   // Orthoses
  
  // Diabetic Supplies
  DMERC_1002A = '10.02A', // Diabetic Shoes
  DMERC_1002B = '10.02B', // Diabetic Supplies
  
  // Miscellaneous Forms
  DMERC_4842 = '484.2',   // Certificate of Medical Necessity
  DMERC_DRORDER = 'DRORDER', // Detailed Written Order
  DMERC_URO = 'URO',      // Urological Supplies
  
  // Updated DME Forms
  DME_0404B = '04.04B',   // Updated Power Wheelchairs
  DME_0404C = '04.04C',   // Updated Power Operated Vehicles
  DME_0603B = '06.03B',   // Updated Enteral Nutrition
  DME_0703A = '07.03A',   // Updated Osteogenesis Stimulators
  DME_0903 = '09.03',     // Updated Orthoses
  DME_1003 = '10.03',     // Updated Diabetic Supplies
  DME_48403 = '484.03'    // Updated Certificate of Medical Necessity
}
